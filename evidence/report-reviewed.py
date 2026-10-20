#!/usr/bin/env python3
"""Validate every retained trial and render all-trial/first-block evidence."""
import argparse,hashlib,json,math
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle,Polygon
from matplotlib.animation import FuncAnimation,PillowWriter
from core import *
from validate import rows,validate_trial

COLORS={'fresh':'#2675a6','missing':'#bc8b22','frozen':'#9b5fa5','restamped':'#ce563d'}


def main():
    p=argparse.ArgumentParser();p.add_argument('root',type=Path);a=p.parse_args();root=a.root.resolve()
    protocol=json.loads((root/'PROTOCOL.json').read_text());records=json.loads((root/'results.json').read_text())
    assert len(records)==len(protocol['schedule'])
    for name,digest in protocol['source_sha256'].items():assert hashlib.sha256((root/'source'/name).read_bytes()).hexdigest()==digest,name
    for name,digest in protocol['input_sha256'].items():assert hashlib.sha256((root/name).read_bytes()).hexdigest()==digest,name
    audits={r['trial']:validate_trial(root,r) for r in records}
    effective=[json.loads((root/r['trial']/'effective-before.json').read_text()) for r in records]
    assert all(v==effective[0] for v in effective),'Runtime configuration differs across trials'
    (root/'EVIDENCE-VALIDATION.json').write_text(json.dumps(dict(passed=True,trials=audits,runtime_parameters_identical=True,source_and_input_hashes_match=True),indent=2))
    table=['| Block | Condition | Goal result | Time (sim s) | Stop after appearance (s) | Min sampled envelope clearance (m) | Contact observed | Arrival requirement |',
           '| --- | --- | --- | --- | --- | --- | --- | --- |']
    for r in records:
        m=r['metrics'];stop='—' if m['stop_after_appearance_s'] is None else '{:.3f}'.format(m['stop_after_appearance_s'])
        table.append('| {} | {} | {} | {:.3f} | {} | {:.3f} | {} | {} |'.format(r['block'],LABELS[r['condition']],r['outcome'],r['elapsed_sim_s'],stop,m['min_sampled_envelope_clearance_m'],'yes' if r['robot_contact_messages'] else 'none observed','pass' if r['endpoint']['settled_position_pass'] else 'fail'))
    summary=[]
    for c in CONDITIONS:
        group=[r for r in records if r['condition']==c]
        summary.append('- {}: goals {}/{} succeeded; contact observed in {}/{}; fixed arrival position {}/{}.'.format(LABELS[c],sum(r['outcome']=='succeeded' for r in group),len(group),sum(r['robot_contact_messages']>0 for r in group),len(group),sum(r['endpoint']['settled_position_pass'] for r in group),len(group)))
    text='\n'.join(['# Robot Failure Lab 05: live topics, frozen observations','',
        'Measured Gazebo/Nav2 simulation. All scheduled trials shown; verification folders are excluded from main counts.','',*table,'','## Condition summaries','',*summary,'',
        '## Method and interpretation','',
        '- AMCL receives fresh scans in every condition. Both costmaps and collision monitor share the same experimental branch. Missing/frozen/restamped policies last two simulated seconds; no navigation setting or timeout differs across conditions.',
        '- Canonical payload hashes cover every LaserScan field except header stamp, excluding transport padding. Raw serialized CDR packets, origin IDs/acquisition times, advertised stamps, publications and independent observer receipts are retained.',
        '- The same stationary obstacle is requested at fault+0.20s. Actual appearance comes from world pose; upstream ray endpoints must show it during the window. Prior map obstacles are unchanged.',
        '- Clearance is sampled distance between a yaw-aware conservative robot envelope and the obstacle box. Zero envelope clearance can occur before physical contact. Obstacle-specific contact messages are separate evidence; the contact stream is event-driven, so absence is not a continuous no-contact certificate.',
        '- Stop requires translation <=0.01m/s and absolute yaw <=0.03rad/s for >=0.3s, with <=0.15s sample gaps. Missing stop is not zero latency. First stop can have multiple causes; costmaps and monitor are not separately isolated.',
        '- Original goal success is distinct from obstacle response. Secondary task-position acceptance is success and <=0.30m world error throughout result+1.0..1.5s. A timeout/failure remains an outcome. No replacement goal or external proximity-stop guard was used.',
        '- Three repeats per condition on one route; Gazebo seeds matched within blocks, AMCL/MPPI/scheduling uncontrolled. No general failure-rate estimate, physical safety validation, complete-scanner failure, Vektor integration or Nav2-defect claim follows.',
        '- Main source/configuration/packages match final verification; contact calibration is separate. Preserve every startup, development check, protocol correction and shutdown anomaly in the archive. Fresh-machine reproduction and public distribution remain unverified.',''])
    (root/'REPORT.md').write_text(text)
    fig,axes=plt.subplots(1,2,figsize=(12,4.8),layout='constrained')
    for c in CONDITIONS:
        group=[r for r in records if r['condition']==c];xs=[r['block'] for r in group]
        axes[0].plot(xs,[r['metrics']['min_sampled_envelope_clearance_m'] for r in group],'o-',color=COLORS[c],label=LABELS[c])
        for r in group:
            if r['robot_contact_messages']:axes[0].scatter(r['block'],r['metrics']['min_sampled_envelope_clearance_m'],marker='x',s=90,color='black',zorder=5)
        durations=[r['elapsed_sim_s'] for r in group]
        axes[1].plot(xs,durations,'o-',color=COLORS[c],label=LABELS[c])
    axes[0].set_title('Sampled envelope clearance · x = observed contact');axes[0].set_ylabel('Minimum conservative-envelope clearance (m)');axes[0].set_ylim(bottom=-.01)
    axes[1].set_title('Original goal time · outcomes in table');axes[1].set_ylabel('Goal to result / deadline (sim seconds)');axes[1].set_ylim(bottom=0)
    for ax in axes:ax.set_xlabel('Block / matched Gazebo seed');ax.set_xticks(sorted({r['block'] for r in records}));ax.grid(alpha=.2);ax.legend(frameon=False,fontsize=8)
    axes[0].text(2,.009,'All three fault conditions overlap at zero',ha='center',fontsize=8)
    axes[1].text(2,56,'All three fault conditions reached the deadline',ha='center',fontsize=8)
    fig.suptitle('Fresh observations, missing messages and frozen payloads\nMeasured simulation · identical navigation configuration',fontsize=13)
    fig.savefig(root/'comparison.png',dpi=160);plt.close(fig)
    block=min(r['block'] for r in records);chosen={c:next(r for r in records if r['block']==block and r['condition']==c) for c in CONDITIONS}
    fig,axes=plt.subplots(4,2,figsize=(12,11),sharex=True,layout='constrained')
    for i,c in enumerate(CONDITIONS):
        r=chosen[c];start=r['window_start'];folder=root/r['trial'];pub=rows(folder/'published.csv');odom=rows(folder/'odom.csv')
        obs=[v for v in pub if v['branch']=='obstacles']
        age_t=[];advertised=[];origin=[]
        for j,v in enumerate(obs):
            if j and v['t']-obs[j-1]['t']>.35:
                age_t.append(float('nan'));advertised.append(float('nan'));origin.append(float('nan'))
            age_t.append(v['t']-start);advertised.append(v['t']-v['stamp']);origin.append(v['t']-v['origin_stamp'])
        axes[i,0].plot(age_t,advertised,color=COLORS[c],label='Advertised age')
        axes[i,0].plot(age_t,origin,'--',color='#222',label='True cached-origin age')
        if c=='missing':axes[i,0].text(1.,.5,'No messages',ha='center',transform=axes[i,0].get_xaxis_transform(),fontsize=9)
        axes[i,0].set_ylabel(LABELS[c]+'\nScan age (s)',fontsize=9)
        axes[i,1].plot([v['stamp']-start for v in odom],[v['speed'] for v in odom],color=COLORS[c],label='Measured odometry speed')
        for ax in axes[i]:ax.axvspan(0,2,color='#d8b389',alpha=.22);ax.axvline(r['appearance']-start,color='#c12940',ls=':');ax.set_xlim(-.6,6);ax.grid(alpha=.15)
        axes[i,1].set_ylabel('Translation (m/s)')
    axes[0,0].legend(frameon=False,fontsize=8);axes[0,1].legend(frameon=False,fontsize=8)
    for ax in axes[-1]:ax.set_xlabel('Sim seconds relative to fault onset')
    fig.suptitle('Predeclared first block · advertised age, actual origin age and motion\nShading: two-second fault/reference window · dotted red: independently confirmed obstacle appearance',fontsize=12)
    fig.savefig(root/'first-block-timeline.png',dpi=150);plt.close(fig)
    fig,axes=plt.subplots(2,2,figsize=(10,7),layout='constrained');artists={};trajectories={}
    for ax,c in zip(axes.flat,CONDITIONS):
        r=chosen[c];trajectories[c]=rows(root/r['trial']/'world.csv')
        trail,=ax.plot([],[],color=COLORS[c]);dot,=ax.plot([],[],'o',color=COLORS[c],ms=7)
        obstacle=Rectangle((OBSTACLE[0]-OBSTACLE_SIZE[0]/2,OBSTACLE[1]-OBSTACLE_SIZE[1]/2),*OBSTACLE_SIZE[:2],facecolor='#333',alpha=0)
        ax.add_patch(obstacle);envelope=Polygon(np.zeros((4,2)),fill=False,edgecolor=COLORS[c]);ax.add_patch(envelope)
        caption=ax.text(.02,.02,'',transform=ax.transAxes,fontsize=8,bbox=dict(facecolor='white',alpha=.9,edgecolor='none'))
        artists[c]=(trail,dot,obstacle,envelope,caption);ax.set_xlim(-1.7,.5);ax.set_ylim(-.1,1.4);ax.set_aspect('equal');ax.set_title(LABELS[c]);ax.grid(alpha=.15);ax.set_xlabel('Gazebo world x (m)');ax.set_ylabel('world y (m)')
    def animate(t):
        result=[]
        for c,r in chosen.items():
            trail,dot,box,envelope,caption=artists[c];data=[v for v in trajectories[c] if r['window_start']-.6<=v['stamp']<=r['window_start']+t]
            if not data:continue
            v=data[-1];trail.set_data([z['x'] for z in data],[z['y'] for z in data]);dot.set_data([v['x']],[v['y']]);envelope.set_xy(rectangle(v['x'],v['y'],v['yaw'],ENVELOPE))
            visible=t>=r['appearance']-r['window_start'];box.set_alpha(.75 if visible else 0)
            caption.set_text('Window {:+.1f}s · {}\nEnvelope clearance: {}\nDark box: introduced obstacle'.format(t,('reference window' if c=='fresh' else 'fault active') if 0<=t<2 else 'original scans',('{:.2f} m'.format(clearance(v)) if visible else 'not present')))
            result.extend((trail,dot,box,envelope,caption))
        return result
    fig.suptitle('Recorded world poses · predeclared first block\nOutline is a conservative envelope; overlap alone is not contact proof',fontsize=12)
    animation=FuncAnimation(fig,animate,frames=np.linspace(-.6,6.,100),interval=100,blit=False)
    animation.save(root/'first-block-recorded.gif',writer=PillowWriter(fps=10),dpi=90);plt.close(fig)
    print('Validated {} outcomes; saved report, two figures and recorded-position animation.'.format(len(records)))


if __name__=='__main__':main()

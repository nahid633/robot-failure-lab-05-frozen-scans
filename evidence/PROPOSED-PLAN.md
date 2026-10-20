---
type: experiment
status: active
updated: 2026-10-20
tags: [vektor, robot-failure-lab, simulation, nav2, sensor-freshness]
sources: [robot-failure-lab-next-experiments-2026-10, robot-failure-lab-03-localization-feed, robot-failure-lab-04-goal-tolerance, robot-failure-lab]
confidence: medium
---

# Robot Failure Lab 05: arriving messages versus fresh observations

## Selection and question

Founder selection on October 20: “lets do it,” referring to the four-condition frozen-LiDAR/new-obstacle proposal in [[robot-failure-lab-next-experiments-2026-10]]. Local implementation, verification, 12 declared main trials and a sharing package are authorized. Publication and outbound messages remain separate.

Question: when an obstacle appears, how do fresh scans, missing scans, repeated old scans with original timestamps, and repeated old scans with misleading new timestamps affect source validity, motion and obstacle response? No collision, failure or specific result is assumed in advance.

## Pre-main protocol and implementation

Separate code: `code/robot-failure-lab/experiment05/`. Preserve all earlier code/evidence. The same two-branch topology supplies AMCL with original scans in every condition and both costmaps/collision monitor with the experimental branch. Baseline goal tolerance 0.25 m, enabled collision monitor, source timeout 1 s and all other navigation parameters remain identical. This is a diagnostic downstream-branch fault, not a complete physical scanner failure or individual-consumer isolation.

Initial verification geometry: original sandbox/start (-2,-0.5)/goal (1,0.5), yaw zero. After >=3 simulated seconds, cross world x=-1.30 with y in [0.25,0.85] while translating >=0.05 m/s for >=0.3 s. Cache the last original pre-window scan and begin a two-second gate. At onset+0.20 s request a stationary box, 0.30 x 0.45 x 0.60 m, at world (-0.60,0.55), z=0.35; it starts parked at (-8,-8). Confirm actual appearance from a separate Gazebo world-pose stream. Placement and sensing must pass separately retained verification before freezing main trials.

Conditions: fresh originals; no obstacle-branch publication; cached scan repeated at upstream cadence with its original stamp; cached payload repeated at upstream cadence with only its header stamp changed to the current upstream acquisition stamp. Log full serialized input/output CDR packets, payload hashes, origin IDs/stamps, publication and receipt times. Do not treat the rewritten timestamp as true acquisition provenance. Restore originals immediately after the half-open two-second interval.

Independent motion/geometry: model world poses at 30 Hz, never injected into navigation TF; retain localized pose separately. Use a conservative model-aligned planar envelope x [-0.20,0.08], y [-0.16,0.16], rotated by measured yaw, which encloses the inspected robot SDF collision shapes. Report its sampled obstacle clearance as an envelope metric; zero envelope clearance is not proof of physical contact. Record obstacle-specific contact messages separately and verify the contact interface with an excluded deliberate simulation overlap. Missing contact messages cannot establish zero collisions.

Primary: source age/provenance/delivery, source-invalid warnings/collision-monitor state, stop latency/distance after actual obstacle appearance, sampled envelope clearance and obstacle-specific contact events. Stop: translation <=0.01 m/s and absolute yaw <=0.03 rad/s for >=0.3 s with <=0.15 s sample gaps. Secondary: original task result, recoveries and unchanged illustrative 0.30 m arrival-position requirement at result+1.0..1.5 s. No independent proximity-stop guard or replacement goal is used.

Initial budgets before main: up to two excluded contact-calibration process attempts and up to eight excluded navigation verification outcomes, including development attempts. The contact budget was revised to four after two retained startup failures and before any navigation outcome. The final four verification outcomes must cover all conditions with matching frozen source/configuration/packages, verified injection, raw laser evidence of the obstacle and meaningful fresh-control obstacle response. If this budget cannot establish instrumentation, retain evidence and revise before any main execution.

Main budget: 12 trials in three seed blocks (101/102/103), cyclic condition orders starting fresh/missing/frozen respectively. Fresh simulator/navigation for each trial, equal 1.5-sim-second pre-goal wait after readiness/audit, a distinct ROS domain per startup and no concurrent simulation workload. AMCL/MPPI/scheduling remain uncontrolled. Freeze all code, models, map, parameters, packages and protocol before main. Do not alter geometry after seeing main outcomes or extend the sample based on results.

Bound startup to 75 wall seconds after worker launch; task to 60 simulated/180 wall seconds; observe through onset+6 s and result+1.8 s, with a 30-wall-second tail watchdog. Task failures/timeouts remain outcomes. Stop on infrastructure/protocol errors; only pre-READY/pre-goal startup failures can continue in new attempt directories (maximum three startups per scheduled trial), retaining all original evidence. Never retry a completed task outcome.

Nine focused tests passed before first calibration: fault boundaries/restoration, timestamp-versus-payload distinction, polygon distance/rotation/touch, sparse/rotating stop rejection, missing-stop handling and nonmutating routing. Python compilation passed. The Lab04 parameter-query and endpoint helpers were copied into the new standalone directory; old code remains unchanged.

## Technical basis

Primary sources retrieved October 20:

- [Jazzy collision-monitor scan handling](https://raw.githubusercontent.com/ros-navigation/navigation2/jazzy/nav2_collision_monitor/src/scan.cpp) and [source age validation](https://raw.githubusercontent.com/ros-navigation/navigation2/jazzy/nav2_collision_monitor/src/source.cpp): scan header age affects source validity. This motivates the contrast, not a measured obstacle outcome.
- [ros_gz bridge service implementation](https://raw.githubusercontent.com/gazebosim/ros_gz/ros2/ros_gz_bridge/src/service_factories/ros_gz_interfaces.cpp): SetEntityPose maps to Gazebo pose requests. Installed interfaces were inspected locally.
- [Gazebo Contact system](https://gazebosim.org/api/sim/8/classgz_1_1sim_1_1systems_1_1Contact.html): contact-sensor support. Empirical calibration is required before using its absence/presence as evidence.

## Execution status and next action

Four excluded calibration-process attempts are retained. The first (`/tmp/robot-failure-lab-05-contact-20261020`, domain 120) exposed unstable hashes caused by CDR transport-padding bytes; canonical field hashing replaced transport-byte hashing and a round-trip test was added. The second (`contact-v2`, domain 122) hit an upstream launch race: Gazebo opened the generated world before xacro produced it. The common launch copy now sequences Gazebo after xacro exits. Neither first nor second attempt reached READY, submitted a goal or performed a contact calibration.

The third (`contact-v3`, domain 124) placed the obstacle into the robot but received no messages on the requested contact topic. Inspection of the Gazebo Contact implementation showed that the topic belongs inside its nested contact element. The fourth (`/tmp/robot-failure-lab-05-contact-v4-20261020`, domain 126) corrected that and passed positive obstacle-specific contact calibration. The Contact implementation emits events only when contact exists; absent messages are not a continuous no-contact certificate. Sources: [Contact implementation](https://raw.githubusercontent.com/gazebosim/gz-sim/gz-sim8/src/systems/contact/Contact.cc), retained logs/source/data and calibration JSON. These are instrumentation revisions before main, not omitted navigation results.

Ten focused tests now pass, including canonical hash stability across CDR round trips. The first navigation verification set (`verification-20261020`, base domain 130) retained two outcomes: fresh control succeeded with 0.171 m minimum sampled envelope clearance; missing scans timed out and produced contact events. It also retained one pre-goal startup failure. The missing outcome exposed that cancellation acknowledgement can arrive after the declared deadline. Revised capture keeps deadline cutoff and cancellation acknowledgement separate and refreshes action status after passive observation. Old evidence remains unchanged and excluded.

An intermediate set (`verification-v2`, base domain 140) retained one fresh-control timeout with 0.142 m minimum envelope clearance and no received contact event, plus a pre-goal parameter-service discovery failure and two missing-condition lifecycle startup timeouts. The frozen scene/fault settings were not changed. Inspection of the local Linux ephemeral port range (32768–60999) and [official ROS domain guidance](https://raw.githubusercontent.com/ros2/ros2_documentation/jazzy/source/Concepts/Intermediate/About-Domain-ID.rst) motivated using lower domains for final verification/main. Port overlap is a plausible infrastructure concern, not an established explanation of every timeout.

Final verification (`verification-v3`, base domain 20) completed four outcomes with identical seven-node live parameter snapshots: all four original goals reached their deadline; fresh scans had 0.129 m minimum envelope clearance and no received contact event; missing/frozen/restamped conditions had zero sampled envelope clearance and received obstacle-specific contact events. Those four outcomes passed full provenance/routing/world/geometry/parameter checks. They are verification evidence, not main results. A goal timeout remains an outcome, not an instrumentation failure. Seven navigation verification outcomes in total (2+1+4) are retained, within the eight-outcome budget; startups are recorded separately.

The frozen main batch launched at `/tmp/robot-failure-lab-05-main-20261020`, base domain 50, using final verification and positive-contact calibration references. Domain selection follows the predeclared distinct-domain-per-start formula. No main outcome is recorded at this entry. Next: complete all 12 declared main trials without changing conditions, independently audit every record, then archive the sharing package. Fresh-machine reproduction, physical performance, Vektor integration and outside use remain unverified.

Related: [[robot-failure-lab]], [[robot-failure-lab-03-localization-feed]], [[robot-failure-lab-04-goal-tolerance]], [[vektor]], [[robotics-attention-playbook-2026-09]].

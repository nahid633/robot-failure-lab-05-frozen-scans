# Robot Failure Lab 05: live topics, frozen observations

Measured Gazebo/Nav2 simulation. All scheduled trials shown; verification folders are excluded from main counts.

| Block | Condition | Goal result | Time (sim s) | Stop after appearance (s) | Min sampled envelope clearance (m) | Contact observed | Arrival requirement |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Fresh scans | succeeded | 50.703 | 0.648 | 0.147 | none observed | pass |
| 1 | Missing scans | timeout | 60.003 | 1.116 | 0.000 | yes | fail |
| 1 | Frozen / original stamp | timeout | 60.015 | 1.224 | 0.000 | yes | fail |
| 1 | Frozen / new stamp | timeout | 60.060 | 2.412 | 0.000 | yes | fail |
| 2 | Missing scans | timeout | 60.057 | 1.188 | 0.000 | yes | fail |
| 2 | Frozen / original stamp | timeout | 60.084 | 1.188 | 0.000 | yes | fail |
| 2 | Frozen / new stamp | timeout | 60.051 | 2.304 | 0.000 | yes | fail |
| 2 | Fresh scans | timeout | 60.048 | 0.684 | 0.130 | none observed | fail |
| 3 | Frozen / original stamp | timeout | 60.042 | 1.224 | 0.000 | yes | fail |
| 3 | Frozen / new stamp | timeout | 60.045 | 2.448 | 0.000 | yes | fail |
| 3 | Fresh scans | succeeded | 34.896 | 24.120 | 0.153 | none observed | pass |
| 3 | Missing scans | timeout | 60.063 | 1.080 | 0.000 | yes | fail |

## Condition summaries

- Fresh scans: goals 2/3 succeeded; contact observed in 0/3; fixed arrival position 2/3.
- Missing scans: goals 0/3 succeeded; contact observed in 3/3; fixed arrival position 0/3.
- Frozen / original stamp: goals 0/3 succeeded; contact observed in 3/3; fixed arrival position 0/3.
- Frozen / new stamp: goals 0/3 succeeded; contact observed in 3/3; fixed arrival position 0/3.

## Method and interpretation

- AMCL receives fresh scans in every condition. Both costmaps and collision monitor share the same experimental branch. Missing/frozen/restamped policies last two simulated seconds; no navigation setting or timeout differs across conditions.
- Canonical payload hashes cover every LaserScan field except header stamp, excluding transport padding. Raw serialized CDR packets, origin IDs/acquisition times, advertised stamps, publications and independent observer receipts are retained.
- The same stationary obstacle is requested at fault+0.20s. Actual appearance comes from world pose; upstream ray endpoints must show it during the window. Prior map obstacles are unchanged.
- Clearance is sampled distance between a yaw-aware conservative robot envelope and the obstacle box. Zero envelope clearance can occur before physical contact. Obstacle-specific contact messages are separate evidence; the contact stream is event-driven, so absence is not a continuous no-contact certificate.
- Stop requires translation <=0.01m/s and absolute yaw <=0.03rad/s for >=0.3s, with <=0.15s sample gaps. Missing stop is not zero latency. First stop can have multiple causes; costmaps and monitor are not separately isolated.
- Original goal success is distinct from obstacle response. Secondary task-position acceptance is success and <=0.30m world error throughout result+1.0..1.5s. A timeout/failure remains an outcome. No replacement goal or external proximity-stop guard was used.
- Three repeats per condition on one route; Gazebo seeds matched within blocks, AMCL/MPPI/scheduling uncontrolled. No general failure-rate estimate, physical safety validation, complete-scanner failure, Vektor integration or Nav2-defect claim follows.
- Main source/configuration/packages match final verification; contact calibration is separate. Preserve every startup, development check, protocol correction and shutdown anomaly in the archive. Fresh-machine reproduction and public distribution remain unverified.

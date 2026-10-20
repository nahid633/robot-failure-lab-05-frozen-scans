# Robot Failure Lab 05: active topics and frozen observations

Measured October 20, 2026. Twelve declared main trials: three each of fresh, missing, frozen-original-stamp and frozen-new-stamp. All retained separately from development/verification.

| Condition | Goals completed | Contact observed during fault | Contact observed later | Min envelope clearance across runs |
| --- | --- | --- | --- | --- |
| Fresh scans | 2/3 | 0/3 | 0/3 | 0.130 m |
| Missing scans | 0/3 | 3/3 | 3/3 | 0.000 m |
| Frozen / original stamp | 0/3 | 3/3 | 2/3 | 0.000 m |
| Frozen / new stamp | 0/3 | 3/3 | 3/3 | 0.000 m |

## Traffic and observation age

| Condition | Messages per two-second window | Maximum advertised age per run | Maximum actual-origin age per run |
| --- | --- | --- | --- |
| Fresh scans | 10–10 | 0.009–0.009 s | 0.009–0.009 s |
| Missing scans | 0–0 | — | — |
| Frozen / original stamp | 10–10 | 2.007–2.007 s | 2.007–2.007 s |
| Frozen / new stamp | 10–10 | 0.012–0.018 s | 2.007–2.007 s |

Missing messages have no applicable advertised-age observation during the window; they are not assigned zero age. The other conditions can have the same publication rate while their actual observation ages differ.

## Motion and contact timing

| Condition | First sustained stop after appearance | First observed contact after appearance |
| --- | --- | --- |
| Fresh scans | 0.648–24.120 s | none observed |
| Missing scans | 1.080–1.188 s | 0.735–0.801 s |
| Frozen / original stamp | 1.188–1.224 s | 0.672–0.753 s |
| Frozen / new stamp | 2.304–2.448 s | 0.714–0.810 s |

These are observed ranges across three runs, not a population estimate. Timing uses independently observed obstacle appearance. Contact can precede the first sustained stop; stopping eventually does not establish avoiding the obstacle.

## What was tested

The same new obstacle appeared in every condition. AMCL kept receiving fresh scans. Both costmaps and collision monitor received the experimental branch. All navigation parameters were identical, including the enabled collision monitor and one-second source timeout. The scene, fault length and obstacle placement stayed fixed after verification.

Full input/output scan packets and canonical hashes distinguish actual cached observation age from the advertised timestamp. Frozen-new-stamp is an explicit synthetic publisher fault. It is not a complete physical scanner failure.

## Read the measurements separately

A message arriving is distinct from fresh observation content. Compare advertised age with actual origin age in DIAGNOSTICS.json and the first-block timeline. Payload repetition alone is not a universal frozen-sensor detector: a stationary scene can also produce similar data. This experiment knows the injected origin and confirms an actual scene change upstream.

Contact observed during the two-second fault and contact during later recovery are separate columns. Contact messages are event-driven; no received contact event is not a continuous no-contact certificate. Positive contact calibration is retained separately. Sampled zero clearance is overlap of a conservative envelope, not itself proof of physical contact.

First sustained stop after appearance can be a later recovery or goal stop. DIAGNOSTICS.json explicitly states whether a qualifying stop occurred before the fault ended. Restored scans, motion response, original-goal completion and fixed arrival acceptance remain separate outcomes.

REPORT.md shows every original goal, including deadlines/timeouts. Three repeats on one route with uncontrolled AMCL/MPPI/scheduling do not establish a general failure rate, physical safety or a Nav2 defect. This remains a standalone experiment without Vektor integration or measured customer use.

## Retained development and execution evidence

Four excluded calibration process attempts preserve the initial transport-padding hash issue, xacro/Gazebo world-generation race, nested contact-topic correction and passing 667-message obstacle-specific positive-contact check. The calibration-start budget was revised from two to four before any navigation outcome. Canonical field hashing now excludes transport padding while original CDR packets remain available.

The first navigation verification set retained fresh/missing outcomes and a pre-goal startup failure. Missing scans produced a deadline and exposed the distinction between deadline cutoff and later cancellation acknowledgement. The recorder was corrected before main execution. An intermediate verification set retained another fresh outcome and additional pre-goal startup errors. Final verification used base domain 20 and main used base 50, keeping startup domains in the [ROS-recommended Linux range](https://raw.githubusercontent.com/ros2/ros2_documentation/jazzy/source/Concepts/Intermediate/About-Domain-ID.rst) after noticing earlier domains overlapped ephemeral ports. That overlap is a plausible infrastructure concern, not an established explanation of every startup error. No scene/fault setting was changed to obtain a different outcome. All seven navigation verification outcomes are excluded from the 12 main counts.

ATTEMPT-AUDIT.json retains every startup, observer error, task/calibration marker and process-death line. Startup failures before a goal are distinct from task failures. Continuations preserve completed task outcomes; source/configuration are frozen for main. Intentional shutdown events are kept without asserting an underlying crash cause.

1 main startup attempt(s) failed before READY/goal; all were retained separately from the 12 task outcomes. Lower domains did not eliminate every startup failure.

## Package

REPORT.md, comparison.png, first-block-timeline.png and first-block-recorded.gif provide the measured explanation. The animation reconstructs world poses from the predeclared first block; it is not physical footage or a simulator screen recording. Protocol, exact sources/model/world/map/configuration/packages, serialized scans, world poses, contact events, parameter audits and all excluded attempts are included.

Fresh-machine reproduction, outside use and public distribution remain unverified. The sharing draft is unsent.

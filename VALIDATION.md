# Publication checks

Checked on 2026-11-09: all imported file hashes match the preserved local archive; Python source parses; root documentation links resolve; files meet GitHub size limits.

Existing tests / measurement checks:

```text
test_half_open_fault_and_fresh_recovery (test_core.Checks.test_half_open_fault_and_fresh_recovery) ... ok
test_invalid_condition (test_core.Checks.test_invalid_condition) ... ok
test_no_motion_stop_is_missing_not_zero_latency (test_core.Checks.test_no_motion_stop_is_missing_not_zero_latency) ... ok
test_overlap_and_touch_are_zero_not_contact_evidence (test_core.Checks.test_overlap_and_touch_are_zero_not_contact_evidence) ... ok
test_payload_hash_survives_cdr_roundtrip_and_padding (test_core.Checks.test_payload_hash_survives_cdr_roundtrip_and_padding) ... ok
test_polygon_clearance_not_center_distance (test_core.Checks.test_polygon_clearance_not_center_distance) ... ok
test_restamping_does_not_change_payload_hash (test_core.Checks.test_restamping_does_not_change_payload_hash) ... ok
test_routing_does_not_mutate_upstream (test_core.Checks.test_routing_does_not_mutate_upstream) ... ok
test_sparse_or_rotating_motion_does_not_count_stop (test_core.Checks.test_sparse_or_rotating_motion_does_not_count_stop) ... ok
test_yaw_changes_envelope_clearance (test_core.Checks.test_yaw_changes_envelope_clearance) ... ok

----------------------------------------------------------------------
Ran 10 tests in 0.082s

OK
```

No new navigation experiment was run. This is not a clean-machine reproduction test.

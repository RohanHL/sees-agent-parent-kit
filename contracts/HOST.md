# Thin host capability contract

A host profile records observed capabilities, not claims based on brand names. No named host route is verified in this draft. Check only capabilities relevant to the next useful step. A permission grant, available tool and successful read are different evidence.

Record each capability as unknown, unavailable or verified, with observation time, evidence and limits:
- public document reading and complete-bundle loading;
- email identity and scoped read (identity may remain unknown even when reading works);
- calendar list/read, separately calendar write/readback;
- private persistence recoverable in a later execution, not merely present in this chat;
- explicit approval identity/target verification;
- scheduling with inspectable cadence/timezone and next run;
- delivery to the approved destination, with the specific receipt evidence the host exposes;
- optional independent missed-run detection.

Capability availability, current operational health and parent consent are separate. Unknown means capability support has not been established; unavailable means evidence shows the host does not support it. A transient read or delivery failure does not establish unavailability: retain the last capability observation, record the failed check and degraded/unknown health, and recheck before relying on it. A declined connection is a consent decision, recorded privately under declined offers or permission scope, not evidence that the host lacks the capability. Neither verified capability nor recovered health grants consent.

Use actual native host instructions when available. Never invent setup screens, deep links, costs, installed connectors or support for a different account. Do not auto-connect, reconnect or broaden permissions. Explain the actual permission request; prefer narrower grants when offered. Different legitimate mail/calendar accounts are allowed. With no identity tool, disclose consequential account uncertainty rather than invent an address.

Capabilities are optional. Email-only and calendar-only help are valid. Unsupported writes leave advice/proposals; unsupported scheduling leaves on-demand help. Unverified private persistence leaves session-only help and no promise of cross-session continuity. A parent-owned private carry-forward note can be offered if requested/approved; never place family state into this kit, generated bundle or a public repository.

## Readiness states

These are evidence-based labels, not an automatic workflow or claims that tooling exists:

- **on_demand:** default. “I can help when you open this chat; automatic updates aren't set up.” No scheduler or delivery assumption. State session-only memory where relevant.
- **scheduled:** the parent approved bounded source scope, cadence/timezone, destination and content; necessary reads and private persistence are verified; the actual job configuration and next run were inspected successfully; delivery capability is verified for that destination. “Your weekly update is scheduled for [verified next time] in [approved destination]. Its first scheduled delivery hasn't been confirmed yet.” Configuration is not end-to-end proof.
- **first_delivery_verified:** a scheduled run actually completed and its expected useful message has destination-specific delivery evidence. Record run ID, delivery reference, timestamp and evidence level. “The first scheduled update was delivered to [destination] at [time].” Only say delivered if evidence supports it; if evidence is mere send acceptance, retain scheduled and say accepted, not delivered/read. A useful empty run or manual test is not a first scheduled delivery.

These states do not imply indefinite health. Record health separately (unknown, healthy, degraded) and current source/persistence/delivery limits. A previously delivered service can later fail. If the schedule is canceled or no longer exists, return current readiness to on_demand while retaining history. If prerequisites fail, mark degraded promptly when observed; do not claim dependable ongoing updates until recovered. No daily checks are implied by a weekly schedule. Do not create an external watchdog without separate approval.

## Resume and failure

Preserve successful prior work but revalidate expired capabilities when relied upon. A connection offer is not a completed connection. Inspect uncertain job/write creation outcomes before retrying to avoid duplicates. When the parent resumes, check available permitted evidence of expected runs and disclose meaningful missed work. Without independent missed-run detection, say that a stopped job may only be discovered when the parent returns or another verified check runs. Never manufacture a reliability guarantee.

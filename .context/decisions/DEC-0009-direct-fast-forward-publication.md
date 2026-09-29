# DEC-0009 — Direct fast-forward publication and canonical baton hashing

Date: 2026-09-29
Status: ACCEPTED
Authority: direct Owner directive plus PP-RM runtime evidence

## Publication

For a prepared commit that is a direct child of the current live `main`, PR creation and merge are not required.

Preferred path:

`fresh-read main -> verify main == prepared parent -> update_ref(main -> prepared commit, force=false) -> fresh-read authoritative state`

If main differs from prepared parent, do not update the ref and do not force. Reconcile/rebuild the change from the new base.

Current prepared commit:
`869b75c509e8cba50a5a61dbd33cf3da4402e8fd`

Current prepared parent:
`cbba4060db543d4a2b800f7c15b2a700e69f6961`

## OCB

No change:
- explicit OSB only;
- maximum three exact-identical attempts;
- no automatic fourth attempt;
- mutation reconciliation required.

## Baton SHA correction

Generation 95 stopped because the declared payload SHA did not match the actual payload.

Canonical rule:
- hash exact payload value bytes encoded UTF-8;
- exclude the `payload=` prefix;
- exclude the trailing newline;
- sender recomputes and verifies before publication;
- receiver computes identically;
- never manually infer a digest.

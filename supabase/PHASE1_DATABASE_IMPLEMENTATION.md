# Bro Code Fashion — Phase 1 database implementation

This document records the Phase 1 database contracts applied to the connected Supabase project on 16 November 2026. The live database migration history is authoritative; do not rerun or recreate the original ten-table schema.

## Applied migrations

- `20261116105456_phase1_order_reservations_and_inventory_operations`
- `20261116105526_phase1_role_based_database_permissions`
- `20261116105540_phase1_storage_roles_and_reservation_expiry_schedule`
- `20261116105653_phase1_restrict_expiry_worker_and_legacy_admin_helper`
- `20261116105720_phase1_policy_cleanup_and_fk_indexes`
- `phase1_admin_user_grants_and_restock_validation` (latest migration; consult Supabase migration history for its generated version)

The earlier permission hardening and owner bootstrap migrations remain applied.

## Database additions

- `reservation_settings`: one configurable setting; initial duration is 30 minutes.
- `inventory_reservations`: one reservation per order item, with variant, quantity, status, expiry, and resolution actor/timestamp.
- `orders`: idempotency key, reservation expiry, WhatsApp reference, confirmation/resolution timestamps, and fulfilment status.
- `inventory_movements`: supports reserve, release, and commit movement types in addition to existing stock movements.
- `private` helper functions enforce active-admin and role checks.

## RPC contracts

- `get_variant_availability(variant_id)`: public availability read for active/published variants; returns on-hand, reserved, available.
- `create_whatsapp_order_request(customer, items, idempotency_key)`: public storefront operation; validates customer details, current product/variant status, current prices, and all stock; creates an order and reserves all lines transactionally.
- `admin_confirm_order(order_id)`: owner/manager; commits stock exactly once.
- `admin_resolve_order(order_id, rejected|cancelled, note)`: owner/manager; releases active reservations.
- `expire_whatsapp_order_requests(limit)`: database-owner/cron worker only; expires pending requests and releases reservations.
- `admin_adjust_inventory(variant_id, quantity_change, reason, restock|adjustment)`: owner/manager; writes stock and audit movement together.
- `admin_set_reservation_duration(minutes)`: owner only; configurable 1–10,080 minutes.

## Role baseline implemented

- Owner: full access and admin-user management.
- Manager: catalogue, inventory, and order operations.
- Staff: read-only access to operational records.
- Anonymous storefront users: read published catalogue/availability and submit WhatsApp order requests; no direct order or stock table access.

## Reservation expiry

A `pg_cron` job named `bcf-expire-whatsapp-reservations` runs every minute and invokes the expiry worker. The worker is not executable by anon or authenticated browser sessions.

## Verification performed

- Transactional create-and-reserve flow.
- Idempotent retry returns the existing order.
- Confirming twice deducts stock only once.
- Expiry releases the reservation.
- Insufficient stock rejects the whole request without creating a partial order or changing stock.
- Rejected requests release their reservation.
- Restock records an audit movement; negative restock is rejected.
- Concurrent requests for the final unit: one succeeds and one is rejected.
- Test fixtures were removed or rolled back; no test product/order records remain.
- Cron job is active and successful runs were observed.

## Known security follow-up

Supabase Security Advisor still reports warnings for intentionally exposed SECURITY DEFINER RPCs used by the storefront and authenticated admin operations, plus leaked-password protection being disabled in Supabase Auth. Review these before production. Do not expose the service-role key in browser code.

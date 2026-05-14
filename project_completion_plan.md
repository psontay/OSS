# OSS (GreenShop) Completion Plan

## Current State vs API Spec (from examplejson.txt & examplejson1.txt)

### Implemented (working):
- JWT login (`/auth/login/`) – returns tokens + user + is_admin
- Token refresh (`/auth/token/refresh/`)
- Profile GET (`/auth/profile/`)
- Home API (`/home/`) – latest 8 plants
- Product list with pagination & filters (category, branch, ph)
- Product detail (stock + sub_images)
- Store locations (GIS)
- Check suitability (GIS)
- Checkout (order creation) – needs verification
- Admin: category CRUD (list, create, detail, delete)
- Admin: plant list, detail, delete (create may lack image handling)
- Admin: stock list, create, detail, delete
- Admin: branch CRUD
- Admin: order list, detail, update-status
- Admin: user list, delete
- Admin dashboard (stats + recent_plants – needs implementation)

### Missing or Incomplete:
1. **User registration** – returns 501 Not Implemented
2. **Profile update (PUT)** – only GET is implemented
3. **Order cancellation** – endpoint exists but controller may be missing
4. **Admin plant creation** – must handle `multipart/form-data` for image upload; current likely expects JSON
5. **Admin dashboard stats** – controller may return placeholder or missing data
6. **Permission checks** – many admin endpoints lack `is_staff` validation
7. **Order checkout validation** – need to ensure stock deduction, total calculation, and proper order item creation
8. **Environment variables** – `.env` missing DB credentials (must be set)
9. **Migrations** – may need to apply or create new migrations for missing fields (e.g., `Plant.image`, `Order.status`, `StoreBranch.location`)

## Implementation Tasks (Ordered by Priority)

### Phase 1: Core Authentication & User Profile
- [ ] 1.1 Implement `register_api` in `auth_controller.py` – create user with hashed password, return success or auto-login token
- [ ] 1.2 Implement `profile_update_api` (PUT/PATCH) to allow updating `first_name`, `last_name`, `phone_number`, `address`
- [ ] 1.3 Add `is_staff` check to all admin endpoints (if not already present)

### Phase 2: Order Workflow
- [ ] 2.1 Review `order_controller.py` – ensure `api_checkout` validates items, checks stock, creates order & order items, deducts stock, returns order ID
- [ ] 2.2 Implement `api_cancel_order` – allow cancellation only if status is PENDING or PROCESSING
- [ ] 2.3 Ensure `api_order_list` returns user's orders with items and status display

### Phase 3: Admin CRUD Completeness
- [ ] 3.1 Fix `admin_plant_controller.plant_create_api` to accept `multipart/form-data` (image upload) and save `PlantImage` instances for sub-images if needed
- [ ] 3.2 Verify `admin_dashboard_api` – compute total_plants, total_orders, total_branches, and fetch 5 most recent plants
- [ ] 3.3 Add missing endpoints: `admin/branches/<id>/` detail view (exists? check), `admin/users/<id>/` detail (optional)

### Phase 4: Data Validation & Error Handling
- [ ] 4.1 Add proper error responses for stock shortage, duplicate entries, foreign key constraints
- [ ] 4.2 Ensure all admin CRUD returns consistent `{status, message, data}` format
- [ ] 4.3 Add input validation (e.g., price > 0, quantity >= 0, valid ph range)

### Phase 5: Testing & Environment
- [ ] 5.1 Configure `.env` with actual database credentials (PostgreSQL with PostGIS for GIS features)
- [ ] 5.2 Run `python manage.py migrate` to create/update tables
- [ ] 5.3 Create superuser for testing
- [ ] 5.4 Test all endpoints with curl or Postman using the API docs as reference

## File Paths Reference
- Main settings: `OSS/settings.py`
- URL config: `OSS/urls.py`
- Controllers: `OSS/controller/*.py`
- Models: `OSS/models/*.py`, `store/models.py`
- Serializers: `OSS/serializers.py`
- Admin controllers: `OSS/controller/admin_*.py`

## Notes
- GIS requires PostgreSQL with PostGIS extension; if not available, fallback or use dummy data.
- Plant images stored in `media/plants/` – ensure MEDIA_ROOT and MEDIA_URL are configured.
- JWT settings can be tuned in `settings.py` (access token lifetime, etc.).

Proceed task by task, marking each as completed in the todo list.

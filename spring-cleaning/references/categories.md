# Conditional category guidance

Use only sections supported by the inventory. A large size is not removal evidence.

| Candidate | Evidence and preferred action | Verification |
| --- | --- | --- |
| Trash and Downloads | Review exact contents and retention needs. Remove only selected items. Being in Trash does not establish authorization to erase everything. | Check selected items and available space after permanent removal. |
| Dependencies and build output | Check project activity, lockfiles, package source access, and local modifications. Identify generated output separately from source or unique downloaded assets. Use the owning tool where practical. | Confirm the retained project can rebuild or reinstall when that check is justified. Report untested recovery. |
| Package or app caches | Check the specific app's documentation and activity. A cache may contain offline or expensive-to-recreate content. Prefer the tool's preview and supported cleanup controls. | Reopen or exercise the affected feature; measure the volume. |
| Device backups | Inspect device, date, and available independent recovery copies. Backups do not regenerate historical state. Use Finder's backup-management controls for selected backups. | Confirm the retained backup remains available; do not claim restore success without testing it. |
| Photos or other valuable libraries | Verify an independent backup and destination capacity. Follow the app's supported move process. Open the copied library successfully before removing the original. | Verify representative content and the library's selected location; a completed copy alone is insufficient. |
| Messages and cloud folders | Use the app's storage controls. Confirm deletion propagation and independent retained copies. Names such as “Folder 2” do not prove duplication. | Compare actual contents and confirm intended sync behavior. Never delete app database internals as a cleanup shortcut. |
| Containers, VMs, and models | Identify the owning app, active use, persistent volumes, snapshots, and unique local data. Prefer selective app-managed removal. Unused images and stopped containers are not necessarily disposable. | Confirm retained workloads or models function; record recovery dependencies and untested conditions. |

For Photos, use [Apple's external-library instructions](https://support.apple.com/en-us/108345).
The destination must use APFS or Mac OS Extended (Journaled), and must not be a
Time Machine backup disk. Hold Option when opening Photos to select a library.
Do not prescribe arbitrary symlinks for app data or cloud-sync databases.

For offloading, inspect the destination and validate the copy before removing the
source. External storage can be disconnected; path absence is not deletion evidence.
APFS snapshots or shared blocks may keep blocks allocated after files disappear.

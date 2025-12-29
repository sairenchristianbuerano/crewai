"""
Migration script from Phase 2 (JSON) to Phase 3 (SQLite).

Migrates error_patterns.json to the learning database while preserving all data.
"""

import os
import json
import shutil
from datetime import datetime
import sys

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from learning_database import LearningDatabase


def migrate_phase2_to_phase3():
    """Migrate Phase 2 error patterns to Phase 3 learning database"""

    print("=" * 80)
    print("Phase 2 → Phase 3 Migration Script")
    print("=" * 80)
    print()

    # Paths
    data_dir = os.path.join(os.path.dirname(__file__), 'data')
    error_patterns_path = os.path.join(data_dir, 'error_patterns.json')
    backup_path = os.path.join(data_dir, f'error_patterns_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json')

    # Step 1: Check if Phase 2 data exists
    if not os.path.exists(error_patterns_path):
        print("ℹ️  No Phase 2 data found (error_patterns.json doesn't exist)")
        print("✅ Creating fresh Phase 3 database...")
        db = LearningDatabase(db_path=os.path.join(data_dir, 'learning.db'))
        print("✅ Phase 3 database initialized successfully")
        return

    # Step 2: Backup Phase 2 data
    print(f"📦 Backing up Phase 2 data to: {os.path.basename(backup_path)}")
    shutil.copy2(error_patterns_path, backup_path)
    print("✅ Backup created")
    print()

    # Step 3: Load Phase 2 data
    print("📖 Loading Phase 2 error patterns...")
    with open(error_patterns_path, 'r') as f:
        phase2_data = json.load(f)

    error_patterns = phase2_data.get('errors', [])
    print(f"✅ Loaded {len(error_patterns)} error patterns from Phase 2")
    print()

    # Step 4: Initialize Phase 3 database
    print("🗄️  Initializing Phase 3 learning database...")
    db = LearningDatabase(db_path=os.path.join(data_dir, 'learning.db'))
    print("✅ Phase 3 database initialized")
    print()

    # Step 5: Migrate error patterns
    if error_patterns:
        print(f"🔄 Migrating {len(error_patterns)} error patterns...")
        db.migrate_error_patterns(error_patterns)
        print("✅ Error patterns migrated successfully")
        print()

        # Display migrated patterns summary
        print("📊 Migration Summary:")
        print("-" * 80)
        analytics = db.get_error_analytics()
        print(f"  Total errors tracked:     {analytics['total_tracked_errors']}")
        print(f"  Unique error patterns:    {analytics['unique_error_patterns']}")
        print()

        if analytics['errors_by_type']:
            print("  Errors by type:")
            for error_type, count in sorted(analytics['errors_by_type'].items(), key=lambda x: x[1], reverse=True):
                print(f"    - {error_type}: {count}")
        print()

    # Step 6: Verify migration
    print("🔍 Verifying migration...")
    overall_metrics = db.get_overall_metrics()
    print(f"✅ Database operational - {overall_metrics['total_generations']} generations recorded")
    print()

    # Step 7: Keep Phase 2 JSON as backup
    print("💾 Phase 2 data preserved:")
    print(f"  - Original: {os.path.basename(error_patterns_path)} (kept for backward compatibility)")
    print(f"  - Backup:   {os.path.basename(backup_path)}")
    print()

    print("=" * 80)
    print("✅ Migration Complete!")
    print("=" * 80)
    print()
    print("Phase 3 Features Now Available:")
    print("  - SQLite database for efficient storage and querying")
    print("  - GET /api/crewai/component-generator/analytics/metrics")
    print("  - GET /api/crewai/component-generator/analytics/insights")
    print("  - GET /api/crewai/component-generator/analytics/trends?days=7")
    print("  - Existing /analytics/errors endpoint (backward compatible)")
    print()
    print("Next Steps:")
    print("  1. Rebuild Docker container: docker-compose build component-generator")
    print("  2. Restart services: docker-compose up -d")
    print("  3. Test new endpoints with curl or browser")
    print()


if __name__ == "__main__":
    try:
        migrate_phase2_to_phase3()
    except Exception as e:
        print(f"\n❌ Migration failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

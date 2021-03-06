package gorm

import (
	"os"
	"testing"

	gGorm "github.com/jinzhu/gorm"

	// goblin
	. "github.com/franela/goblin"
)

const sqliteFile = "/tmp/schema_test_2008.sql"

func setup() *gGorm.DB {
	db, _ := gGorm.Open("sqlite3", sqliteFile)
	return db
}

func teardown(db *gGorm.DB) {
	db.Close()
	os.Remove(sqliteFile)
}

func TestMigrationSchema(t *testing.T) {
	g := Goblin(t)

	var db *gGorm.DB
	var drv *Driver

	g.Describe("MigrationSchema", func() {
		g.Before(func() {
			db = setup()
			drv = &Driver{
				DB: db,
			}
		})

		g.After(func() {
			teardown(db)
		})

		g.It("should migrate up /no error", func() {
			err := drv.SchemaUp()
			g.Assert(err).Equal(nil)
		})

		g.It("should migrate down /no error", func() {
			err := drv.SchemaDown()
			g.Assert(err).Equal(nil)
		})
	})
}

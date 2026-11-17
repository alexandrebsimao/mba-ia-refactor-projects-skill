const db = require('../database/connection');

class CourseModel {
    static async findById(id) {
        return db.get("SELECT * FROM courses WHERE id = ? AND active = 1", [id]);
    }

    static async findAll() {
        return db.all("SELECT * FROM courses");
    }
}

module.exports = CourseModel;

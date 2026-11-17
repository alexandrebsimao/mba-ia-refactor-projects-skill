const db = require('../database/connection');

class EnrollmentModel {
    static async create(userId, courseId) {
        const result = await db.run(
            "INSERT INTO enrollments (user_id, course_id) VALUES (?, ?)",
            [userId, courseId]
        );
        return result.lastID;
    }

    static async findByCourse(courseId) {
        return db.all("SELECT * FROM enrollments WHERE course_id = ?", [courseId]);
    }
}

module.exports = EnrollmentModel;

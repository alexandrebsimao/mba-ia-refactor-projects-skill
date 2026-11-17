const db = require('../database/connection');

class PaymentModel {
    static async create(enrollmentId, amount, status) {
        const result = await db.run(
            "INSERT INTO payments (enrollment_id, amount, status) VALUES (?, ?, ?)",
            [enrollmentId, amount, status]
        );
        return result.lastID;
    }

    static async findByEnrollment(enrollmentId) {
        return db.get("SELECT * FROM payments WHERE enrollment_id = ?", [enrollmentId]);
    }
}

module.exports = PaymentModel;

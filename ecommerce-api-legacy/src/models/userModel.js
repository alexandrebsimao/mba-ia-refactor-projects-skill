const db = require('../database/connection');

class UserModel {
    static async findById(id) {
        return db.get("SELECT id, name, email FROM users WHERE id = ?", [id]);
    }

    static async findByEmail(email) {
        return db.get("SELECT * FROM users WHERE email = ?", [email]);
    }

    static async create(name, email, passwordHash) {
        const result = await db.run(
            "INSERT INTO users (name, email, pass) VALUES (?, ?, ?)",
            [name, email, passwordHash]
        );
        return result.lastID;
    }

    static async deleteWithCascade(id) {
        await db.run("BEGIN TRANSACTION");
        try {
            await db.run(
                "DELETE FROM payments WHERE enrollment_id IN (SELECT id FROM enrollments WHERE user_id = ?)",
                [id]
            );
            await db.run("DELETE FROM enrollments WHERE user_id = ?", [id]);
            await db.run("DELETE FROM users WHERE id = ?", [id]);
            await db.run("COMMIT");
            return true;
        } catch (err) {
            await db.run("ROLLBACK");
            throw err;
        }
    }
}

module.exports = UserModel;

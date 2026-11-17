const db = require('../database/connection');

class ReportController {
    static async getFinancialReport(req, res, next) {
        try {
            const query = `
                SELECT
                    c.id as course_id,
                    c.title as course_title,
                    u.name as student_name,
                    p.amount as payment_amount,
                    p.status as payment_status
                FROM courses c
                LEFT JOIN enrollments e ON e.course_id = c.id
                LEFT JOIN users u ON u.id = e.user_id
                LEFT JOIN payments p ON p.enrollment_id = e.id
                ORDER BY c.id
            `;

            const rows = await db.all(query);

            const coursesMap = new Map();

            for (const row of rows) {
                if (!coursesMap.has(row.course_id)) {
                    coursesMap.set(row.course_id, {
                        course: row.course_title,
                        revenue: 0,
                        students: []
                    });
                }

                const courseData = coursesMap.get(row.course_id);

                if (row.student_name !== null) {
                    const paidAmount = (row.payment_status === 'PAID') ? (row.payment_amount || 0) : 0;
                    if (row.payment_status === 'PAID') {
                        courseData.revenue += row.payment_amount;
                    }
                    courseData.students.push({
                        student: row.student_name || 'Unknown',
                        paid: row.payment_amount || 0
                    });
                }
            }

            const report = Array.from(coursesMap.values());
            return res.json(report);
        } catch (err) {
            next(err);
        }
    }
}

module.exports = ReportController;

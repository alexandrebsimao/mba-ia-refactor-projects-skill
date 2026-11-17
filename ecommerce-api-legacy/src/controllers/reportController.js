const ReportModel = require('../models/reportModel');

class ReportController {
    static async getFinancialReport(req, res, next) {
        try {
            const rows = await ReportModel.getFinancialReportRows();
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
                    if (row.payment_status === 'PAID') {
                        courseData.revenue += row.payment_amount;
                    }
                    courseData.students.push({
                        student: row.student_name || 'Unknown',
                        paid: row.payment_amount || 0
                    });
                }
            }

            return res.json(Array.from(coursesMap.values()));
        } catch (err) {
            next(err);
        }
    }
}

module.exports = ReportController;

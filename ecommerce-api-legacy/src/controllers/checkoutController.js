const CourseModel = require('../models/courseModel');
const UserModel = require('../models/userModel');
const EnrollmentModel = require('../models/enrollmentModel');
const PaymentModel = require('../models/paymentModel');
const AuditLogModel = require('../models/auditLogModel');
const PaymentService = require('../services/paymentService');
const { hashPassword } = require('../services/cryptoService');
const cacheService = require('../services/cacheService');

class CheckoutController {
    static async checkout(req, res, next) {
        try {
            const { usr: userName, eml: email, pwd: password, c_id: courseId, card: creditCard } = req.body;

            if (!userName || !email || !courseId || !creditCard) {
                return res.status(400).send("Bad Request");
            }

            const course = await CourseModel.findById(courseId);
            if (!course) {
                return res.status(404).send("Curso não encontrado");
            }

            let user = await UserModel.findByEmail(email);
            let userId;

            if (!user) {
                const passHash = hashPassword(password || "123456");
                userId = await UserModel.create(userName, email, passHash);
            } else {
                userId = user.id;
            }

            const paymentResult = PaymentService.processPayment(creditCard, course.price);
            if (paymentResult.status === "DENIED") {
                return res.status(400).send("Pagamento recusado");
            }

            const enrollmentId = await EnrollmentModel.create(userId, courseId);
            await PaymentModel.create(enrollmentId, course.price, paymentResult.status);
            await AuditLogModel.create(`Checkout curso ${courseId} por ${userId}`);

            cacheService.set(`last_checkout_${userId}`, course.title);

            return res.status(200).json({ msg: "Sucesso", enrollment_id: enrollmentId });
        } catch (err) {
            next(err);
        }
    }
}

module.exports = CheckoutController;

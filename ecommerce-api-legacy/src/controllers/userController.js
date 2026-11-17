const UserModel = require('../models/userModel');

class UserController {
    static async deleteUser(req, res, next) {
        try {
            const { id } = req.params;
            await UserModel.deleteWithCascade(id);
            return res.send("Usuário deletado, mas as matrículas e pagamentos ficaram sujos no banco.");
        } catch (err) {
            next(err);
        }
    }
}

module.exports = UserController;

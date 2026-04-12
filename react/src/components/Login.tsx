function Login() {
    return (
        <div className = "login-container">
            <div className = "login-card">
                <div className="mb-3">
                    <label htmlFor="email">Email</label>
                    <input
                        type="email"
                        id="email"
                        className="form-control"
                        placeholder="Enter email"
                    />
                </div>
                <div className="mb-3">
                    <label htmlFor="password">Password</label>
                    <input
                        type="password"
                        id="password"
                        className="form-control"
                        placeholder="Enter password"
                    />
                </div>

                <button className="btn btn-primary w-100">Login</button>
            </div>
        </div>
    );
}

export default Login;

import { useState } from "react";
import { toast, ToastContainer } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";

const Login = ({ onLogin }) => {
  const [usernameOrEmail, setUsernameOrEmail] = useState("");
  const [password, setPassword] = useState("");
  const [rememberMe, setRememberMe] = useState(false);
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState({});

  const validate = () => {
    const newErrors = {};
    if (!usernameOrEmail.trim()) {
      newErrors.usernameOrEmail = "Username or Email is required";
    } else if (
      usernameOrEmail.includes("@") &&
      !/^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i.test(usernameOrEmail)
    ) {
      newErrors.usernameOrEmail = "Invalid email address";
    }
    if (!password) {
      newErrors.password = "Password is required";
    } else if (password.length < 6) {
      newErrors.password = "Password must be at least 6 characters";
    }
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!validate()) {
      toast.error("Please fix the errors in the form.");
      return;
    }
    setLoading(true);

    // Check for hardcoded credentials
    if (usernameOrEmail === "mithun" && password === "mithun@07") {
      setTimeout(() => {
        setLoading(false);
        toast.success("Login successful! Redirecting to dashboard...");
        onLogin();
      }, 1000);
      return;
    }

    // Simulate login API call for other credentials
    setTimeout(() => {
      setLoading(false);
      toast.error("Invalid username or password.");
      // Clear password field after failed login
      setPassword("");
    }, 1500);
  };

  return (
    <div className="login-container">
      <ToastContainer position="top-center" />
      <h1 className="login-title">Login</h1>
      <form onSubmit={handleSubmit} noValidate>
        <div className={`form-group ${errors.usernameOrEmail ? "error" : ""}`}>
          <label htmlFor="usernameOrEmail">Username or Email</label>
          <input
            type="text"
            id="usernameOrEmail"
            name="usernameOrEmail"
            placeholder="Enter username or email"
            value={usernameOrEmail}
            onChange={(e) => setUsernameOrEmail(e.target.value)}
            aria-describedby="usernameOrEmailError"
            aria-invalid={errors.usernameOrEmail ? "true" : "false"}
          />
          {errors.usernameOrEmail && (
            <span id="usernameOrEmailError" className="error-message">
              {errors.usernameOrEmail}
            </span>
          )}
        </div>

        <div className={`form-group ${errors.password ? "error" : ""}`}>
          <label htmlFor="password">Password</label>
          <input
            type="password"
            id="password"
            name="password"
            placeholder="Enter password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            aria-describedby="passwordError"
            aria-invalid={errors.password ? "true" : "false"}
          />
          {errors.password && (
            <span id="passwordError" className="error-message">
              {errors.password}
            </span>
          )}
        </div>

        <div className="form-group remember-me">
          <input
            type="checkbox"
            id="rememberMe"
            name="rememberMe"
            checked={rememberMe}
            onChange={(e) => setRememberMe(e.target.checked)}
          />
          <label htmlFor="rememberMe">Remember me</label>
        </div>

        <button type="submit" className="login-btn" disabled={loading}>
          {loading ? "Logging in..." : "Login"}
        </button>

        <div className="forgot-password">
          <a href="#forgot-password">Forgot password?</a>
        </div>
      </form>
    </div>
  );
};

export default Login;

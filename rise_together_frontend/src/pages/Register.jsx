import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import AuthLayout from "../components/AuthLayout";
import { Eye, EyeOff, Loader2, UserPlus } from "lucide-react";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Label } from "../components/ui/label";
import API from "../lib/api";
import { useAuth } from "../context/AuthContext";

const Register = () => {
  const navigate = useNavigate();
  const { login } = useAuth();
  const [showPassword, setShowPassword] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const [form, setForm] = useState({
    name: "",
    email: "",
    password: "",
    confirmPassword: "",
  });

  const [error, setError] = useState("");

  const handleChange = (e) => {
    setForm({
      ...form,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setIsSubmitting(true);

    const { name, email, password, confirmPassword } = form;

    // 1 validation
    if (!name || !email || !password || !confirmPassword) {
      setError("All fields are required");
      setIsSubmitting(false);
      return;
    }

    if (password !== confirmPassword) {
      setError("Passwords do not match");
      setIsSubmitting(false);
      return;
    }
    //2.register user
   try{
    const registerRes=await API.post("/auth/register",{
      name,
      email,
      password
    });
    const {access_token}=registerRes.data;

    // Store in localStorage so the request interceptor automatically picks it up
    localStorage.setItem("token", access_token);

    //4.fetch the loggen-in user profile
    const userRes=await API.get("/auth/self");
     
    //5. store user session globally and redirect
    login(access_token, userRes.data);
    setIsSubmitting(false);
    navigate("/learning-paths");
      } catch (error) {
     const detail = error.response?.data?.detail;
     const msg = Array.isArray(detail)
       ? detail.map((e) => e.msg).join(", ")
       : (detail || error.message || "Registration failed");
       
     setError(msg);
     setIsSubmitting(false);
   }
   };


  const labelCls = "text-[color:var(--brand-indigo)] font-semibold";
  const inputCls = "h-11 rounded-xl";

  return (
    <AuthLayout
      title="Create your account"
      subtitle="Start your learning journey with Rise Together"
      footer={
        <>
          Already have an account?{" "}
          <Link
            to="/login"
            className="font-medium text-[color:var(--brand-indigo)] underline-offset-4 hover:underline"
          >
            Sign in
          </Link>
        </>
      }
    >
      <form onSubmit={handleSubmit} className="space-y-5" noValidate>
        <div className="space-y-2">
          <Label htmlFor="name" className={labelCls}>Full name</Label>
          <Input
            id="name"
            name="name"
            type="text"
            autoComplete="name"
            placeholder="Priya Sharma"
            value={form.name}
            onChange={handleChange}
            className={inputCls}
          />
        </div>

        <div className="space-y-2">
          <Label htmlFor="email" className={labelCls}>Email</Label>
          <Input
            id="email"
            name="email"
            type="email"
            autoComplete="email"
            placeholder="you@college.edu"
            value={form.email}
            onChange={handleChange}
            className={inputCls}
          />
        </div>

        <div className="space-y-2">
          <Label htmlFor="password" className={labelCls}>Password</Label>
          <div className="relative">
            <Input
              id="password"
              name="password"
              type={showPassword ? "text" : "password"}
              autoComplete="new-password"
              placeholder="At least 8 characters"
              value={form.password}
              onChange={handleChange}
              className="h-11 rounded-xl pr-11"
            />
            <button
              type="button"
              onClick={() => setShowPassword((s) => !s)}
              className="absolute inset-y-0 right-0 grid w-11 place-items-center text-muted-foreground hover:text-[color:var(--brand-indigo)]"
              aria-label={showPassword ? "Hide password" : "Show password"}
            >
              {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
            </button>
          </div>
        </div>

        <div className="space-y-2">
          <Label htmlFor="confirmPassword" className={labelCls}>Confirm password</Label>
          <Input
            id="confirmPassword"
            name="confirmPassword"
            type={showPassword ? "text" : "password"}
            autoComplete="new-password"
            placeholder="Re-enter your password"
            value={form.confirmPassword}
            onChange={handleChange}
            className={inputCls}
          />
        </div>

        {error && (
          <div
            role="alert"
            className="rounded-lg border border-red-500/30 bg-red-500/10 px-4 py-3 text-sm text-red-500"
          >
            {error === "An account with that email already exists" ? (
              <span>
                An account with that email already exists.{" "}
                <Link to="/login" className="font-bold underline ml-1 hover:text-red-700 transition-colors">
                  Sign in instead
                </Link>
              </span>
            ) : (
              error
            )}
          </div>
        )}

        <Button
          type="submit"
          disabled={isSubmitting}
          className="h-11 w-full rounded-xl font-semibold text-white transition-all hover:opacity-95 hover:shadow-[var(--shadow-elegant)] flex items-center justify-center gap-1.5"
          style={{ background: "var(--gradient-button)" }}
        >
          {isSubmitting ? (
            <>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" /> Creating account…
            </>
          ) : (
            <>
              <UserPlus className="h-4 w-4" /> Create account
            </>
          )}
        </Button>

        <p className="text-xs text-muted-foreground">
          By creating an account you agree to our Terms and acknowledge our Privacy Policy.
        </p>
      </form>
    </AuthLayout>
  );
};

export default Register;
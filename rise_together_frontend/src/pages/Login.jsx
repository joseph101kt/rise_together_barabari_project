import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import AuthLayout from "../components/AuthLayout";
import { Eye, EyeOff, Loader2, LogIn } from "lucide-react";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Label } from "../components/ui/label";
import API from "../lib/api";
import { useAuth } from "../context/AuthContext";

const Login = () => {
  const navigate = useNavigate();
  const { login } = useAuth();
  const [showPassword, setShowPassword] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const [form, setForm] = useState({
    email: "",
    password: "",
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

    const { email, password } = form;
      //1. validation 
    if (!email || !password) {
      setError("All fields are required");
      setIsSubmitting(false);
      return;
    }

    try{
      //2.call login API 
      const loginRes=await API.post("/auth/login",{
        email,
        password,
      });
      //3.save the JWT and user data to global auth state
      const {access_token}=loginRes.data;
      
      // Store in localStorage so the request interceptor automatically picks it up
      localStorage.setItem("token", access_token);
      
      //4. fetch the logged in profile
      const userRes=await API.get("/auth/self");
      
      login(access_token, userRes.data);
      setIsSubmitting(false);
      navigate("/learning-paths");

      } catch (error) {
      // Parse backend errors
      const detail = error.response?.data?.detail;
      const msg = Array.isArray(detail)
        ? detail.map((e) => e.msg).join(", ")
        : (detail || error.message || "Invalid email or password");
      setError(msg);
      setIsSubmitting(false);
    } 
  };


  return (
    <AuthLayout
      title="Welcome back"
      subtitle="Sign in to continue your learning path."
      footer={
        <>
          New here?{" "}
          <Link
            to="/register"
            className="font-medium text-[color:var(--brand-indigo)] underline-offset-4 hover:underline"
          >
            Create an account
          </Link>
        </>
      }
    >
      <form onSubmit={handleSubmit} className="space-y-5" noValidate>
        <div className="space-y-2">
          <Label htmlFor="email" className="text-[color:var(--brand-indigo)] font-semibold">
            Email
          </Label>
          <Input
            id="email"
            name="email"
            type="email"
            autoComplete="email"
            placeholder="you@college.edu"
            value={form.email}
            onChange={handleChange}
            className="h-11 rounded-xl"
          />
        </div>

        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <Label htmlFor="password" className="text-[color:var(--brand-indigo)] font-semibold">
              Password
            </Label>
            <Link
              to="/"
              className="text-xs font-medium text-[color:var(--brand-indigo)] underline-offset-4 hover:underline"
            >
              Forgot password?
            </Link>
          </div>
          <div className="relative">
            <Input
              id="password"
              name="password"
              type={showPassword ? "text" : "password"}
              autoComplete="current-password"
              placeholder="••••••••"
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

        {error && (
          <div
            role="alert"
            className="rounded-lg border border-red-500/30 bg-red-500/10 px-3 py-2 text-sm text-red-500"
          >
            {error}
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
              <Loader2 className="mr-2 h-4 w-4 animate-spin" /> Signing in…
            </>
          ) : (
            <>
              <LogIn className="h-4 w-4" /> Sign in
            </>
          )}
        </Button>
      </form>
    </AuthLayout>
  );
};

export default Login;

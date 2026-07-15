import React from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

const Logo = ({ className = "" }) => {
  const auth = useAuth();
  const destination = auth?.isAuthenticated ? "/learning-paths" : "/";

  return (
    <Link to={destination} className={`inline-flex items-center gap-2 ${className ?? ""}`}>
      <span className="grid h-8 w-8 place-items-center rounded-lg bg-primary text-primary-foreground font-display font-bold">
        R
      </span>
      <span className="font-display text-xl font-semibold tracking-tight">
        Rise Together
      </span>
    </Link>
  );
};

export default Logo;

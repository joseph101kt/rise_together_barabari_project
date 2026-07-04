import React from "react";
import { Navigate, Outlet } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import Loader from "./ui/Loader";

const ProtectedRoute = () => {
  const { isAuthenticated, loading } = useAuth();

  // Show a loading screen while initializing authentication state
  if (loading) {
    return <Loader fullPage />;
  }


  // If not authenticated, redirect the user to the landing page
  if (!isAuthenticated) {
    return <Navigate to="/" replace />;
  }

  // If authenticated, render the child routes
  return <Outlet />;
};

export default ProtectedRoute;
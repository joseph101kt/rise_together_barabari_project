import React from "react";
import { Routes, Route, Navigate } from "react-router-dom";

// Page Imports
import Home from "./pages/Home";
import Register from "./pages/Register";
import Login from "./pages/Login";
import LearningPaths from "./pages/LearningPaths";
import PathDetails from "./pages/PathDetails";
import PublicProfile from "./pages/PublicProfile";
import NotFound from "./pages/NotFound";

import ProtectedRoute from "./components/ProtectedRoute";
import { AuthProvider } from "./context/AuthContext";

const App = () => {
  return (
    <AuthProvider>
      <Routes>
        {/* Default Route — Home landing page */}
        <Route path="/" element={<Home />} />

        {/* Auth Routes */}
        <Route path="/register" element={<Register />} />
        <Route path="/login" element={<Login />} />
        {/* Grouped Protected Routes */}
        <Route element={<ProtectedRoute />}>
          <Route path="/learning-paths" element={<LearningPaths />} />
          <Route path="/learning-paths/:id" element={<PathDetails />} />
          <Route path="/profile/:id" element={<PublicProfile />} />
        </Route>
    
        {/*Catch all Other routes for 404 not found  */}
        <Route path="*" element={<NotFound />} />
      </Routes>
    </AuthProvider>
  );
};

export default App;
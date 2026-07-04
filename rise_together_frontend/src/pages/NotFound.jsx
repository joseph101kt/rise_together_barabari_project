import React from "react";
import { Link } from "react-router-dom";
import { Button } from "../components/ui/button";

const NotFound = () => {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-background px-4 text-center">
      <div className="space-y-6">
        {/* 404 Heading using brand indigo color */}
        <h1 className="font-display text-9xl font-bold tracking-tighter text-[color:var(--brand-indigo)] animate-bounce">
          404
        </h1>
        <div className="space-y-2">
          <h2 className="text-2xl font-bold tracking-tight text-foreground">
            Page Not Found
          </h2>
          <p className="text-muted-foreground max-w-sm mx-auto">
            Sorry, we couldn't find the page you are looking for. 
          </p>
        </div>
        
        {/* Button to go back home */}
        <Button 
          asChild 
          className="h-11 rounded-xl px-8 font-semibold text-white transition-all hover:opacity-95" 
          style={{ background: "var(--gradient-button)" }}
        >
          <Link to="/">
            Go back home
          </Link>
        </Button>
      </div>
    </div>
  );
};

export default NotFound;

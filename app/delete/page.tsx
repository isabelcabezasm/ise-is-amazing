"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { ArrowLeft, Lock, Trash2, AlertTriangle } from "lucide-react";
import Link from "next/link";
import { AMAZING_API_URL } from "@/lib/api-config";

export default function DeletePage() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [message, setMessage] = useState("");
  const [messageType, setMessageType] = useState<"success" | "error" | "">("");

  // Simple authentication - check against environment variables or hardcoded values
  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setMessage("");

    // Simple authentication - you can set these environment variables
    // For demo purposes, using simple credentials
    const validUsername = process.env.NEXT_PUBLIC_ADMIN_USERNAME || "login_admin";
    const validPassword = process.env.NEXT_PUBLIC_ADMIN_PASSWORD || "amazing_password_123";

    if (username === validUsername && password === validPassword) {
      setIsAuthenticated(true);
      setMessage("Authentication successful!");
      setMessageType("success");
    } else {
      setMessage("Invalid username or password");
      setMessageType("error");
    }

    setIsLoading(false);
  };

  const handleDeleteAll = async () => {
    if (!window.confirm("Are you sure you want to delete ALL amazing messages? This action cannot be undone!")) {
      return;
    }

    setIsLoading(true);
    setMessage("");

    try {
      const response = await fetch(AMAZING_API_URL, {
        method: 'DELETE',
      });

      if (response.ok) {
        setMessage("All messages have been successfully deleted!");
        setMessageType("success");
      } else {
        throw new Error('Failed to delete messages');
      }
    } catch (error) {
      console.error('Error deleting messages:', error);
      setMessage("Failed to delete messages. Please try again.");
      setMessageType("error");
    } finally {
      setIsLoading(false);
    }
  };

  const handleLogout = () => {
    setIsAuthenticated(false);
    setUsername("");
    setPassword("");
    setMessage("");
    setMessageType("");
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-red-50 to-orange-100 p-4">
      <div className="max-w-md mx-auto space-y-6">
        {/* Header */}
        <div className="text-center space-y-2">
          <div className="flex items-center justify-center gap-4 mb-4">
            <Link
              href="/amazing"
              className="inline-flex items-center gap-1 text-gray-600 hover:text-gray-800 text-sm font-medium transition-colors"
            >
              <ArrowLeft className="h-4 w-4" />
              <span>Back to Amazing</span>
            </Link>
          </div>
          <div className="flex items-center justify-center gap-2 mb-4">
            <Lock className="h-8 w-8 text-red-600" />
            <h1 className="text-3xl font-bold text-gray-900">Admin Panel</h1>
          </div>
          <p className="text-gray-600">
            Authentication required for administrative actions
          </p>
        </div>

        {!isAuthenticated ? (
          /* Login Form */
          <Card className="border-red-200">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-red-700">
                <Lock className="h-5 w-5" />
                Login Required
              </CardTitle>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleLogin} className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="username">Username</Label>
                  <Input
                    id="username"
                    type="text"
                    placeholder="Enter username"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    required
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="password">Password</Label>
                  <Input
                    id="password"
                    type="password"
                    placeholder="Enter password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                  />
                </div>
                <Button 
                  type="submit" 
                  className="w-full"
                  disabled={isLoading}
                >
                  {isLoading ? "Authenticating..." : "Login"}
                </Button>
              </form>
            </CardContent>
          </Card>
        ) : (
          /* Admin Panel */
          <Card className="border-red-200">
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                <span className="flex items-center gap-2 text-red-700">
                  <Trash2 className="h-5 w-5" />
                  Danger Zone
                </span>
                <Button 
                  variant="outline" 
                  size="sm" 
                  onClick={handleLogout}
                  className="text-sm"
                >
                  Logout
                </Button>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <Alert className="border-orange-200 bg-orange-50">
                <AlertTriangle className="h-4 w-4 text-orange-600" />
                <AlertDescription className="text-orange-800">
                  <strong>Warning:</strong> This action will permanently delete all amazing messages from the database. This cannot be undone!
                </AlertDescription>
              </Alert>

              <div className="space-y-4">
                <div className="p-4 border border-red-200 rounded-lg bg-red-50">
                  <h3 className="font-medium text-red-900 mb-2">Delete All Messages</h3>
                  <p className="text-sm text-red-700 mb-4">
                    This will remove all &ldquo;You are amazing&rdquo; messages from all languages, including their repetition counts.
                  </p>
                  <Button 
                    variant="destructive" 
                    onClick={handleDeleteAll}
                    disabled={isLoading}
                    className="w-full flex items-center gap-2"
                  >
                    <Trash2 className="h-4 w-4" />
                    {isLoading ? "Deleting..." : "Delete All Messages"}
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Status Messages */}
        {message && (
          <Alert className={messageType === "success" ? "border-green-200 bg-green-50" : "border-red-200 bg-red-50"}>
            <AlertDescription className={messageType === "success" ? "text-green-800" : "text-red-800"}>
              {message}
            </AlertDescription>
          </Alert>
        )}

        {/* Footer */}
        <div className="text-center text-gray-500 text-sm py-4">
          <p>Administrative access for managing amazing messages</p>
        </div>
      </div>
    </div>
  );
}

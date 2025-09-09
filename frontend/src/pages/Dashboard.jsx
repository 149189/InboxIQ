/* eslint-disable no-undef */
// src/pages/Dashboard.jsx
import React, { useEffect, useState } from "react";
import { Button, CircularProgress, Typography, Box } from "@mui/material";
import { useNavigate } from "react-router-dom";

export default function Dashboard() {
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        // First, sync session to ensure proper authentication state
        console.log("Syncing session...");
        const syncRes = await fetch("/auth/sync-session/", {
          method: "GET",
          credentials: "include",
          headers: {
            Accept: "application/json",
          },
        });

        if (syncRes.ok) {
          const syncData = await syncRes.json();
          console.log("Session sync result:", syncData);
          
          if (syncData.authenticated) {
            // If already authenticated from sync, use that data
            setProfile(syncData.user);
            setLoading(false);
            return;
          }
        }

        // If sync didn't return authenticated user, try profile endpoint
        console.log("Fetching profile...");
        const res = await fetch("/auth/oauth/profile/", {
          method: "GET",
          credentials: "include", // include cookies (sessionid)
          headers: {
            Accept: "application/json",
          },
        });

        if (!res.ok) {
          if (res.status === 401) {
            throw new Error("Not authenticated. Please log in again.");
          }
          throw new Error(`Profile fetch failed with status: ${res.status}`);
        }

        const data = await res.json();
        setProfile(data);
      } catch (err) {
        console.error("Profile error:", err);
        setError(err.message);

        // redirect after short delay if not authenticated
        if (err.message.includes("Not authenticated")) {
          setTimeout(() => navigate("/login?error=session_expired"), 2000);
        }
      } finally {
        setLoading(false);
      }
    };

    fetchProfile();
  }, [navigate]);

  const handleLogout = async () => {
    try {
      await fetch("/auth/logout/", {
        method: "POST",
        credentials: "include",
        headers: {
          "Content-Type": "application/json",
        },
      });

      sessionStorage.clear();
      localStorage.clear();
      navigate("/login?message=logged_out");
    } catch (err) {
      console.error("Logout failed:", err);
      navigate("/login");
    }
  };

  if (loading) {
    return (
      <Box display="flex" flexDirection="column" justifyContent="center" alignItems="center" height="50vh">
        <CircularProgress size={60} />
        <Typography variant="body1" sx={{ mt: 2 }}>
          Loading your profile...
        </Typography>
      </Box>
    );
  }

  if (error) {
    return (
      <Box textAlign="center" mt={10} px={4}>
        <Typography variant="h5" color="error" gutterBottom>
          Unable to Load Profile
        </Typography>
        <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
          {error}
        </Typography>
        <Button variant="contained" onClick={() => navigate("/login")}>
          Go to Login
        </Button>
      </Box>
    );
  }

  return (
    <Box textAlign="center" mt={10} px={4}>
      {profile?.profile_picture && (
        <img
          src={profile.profile_picture}
          alt="Profile"
          style={{
            width: 80,
            height: 80,
            borderRadius: "50%",
            marginBottom: 16,
          }}
        />
      )}

      <Typography variant="h4" gutterBottom>
        Hello {profile?.name || profile?.email || "User"} 👋
      </Typography>

      <Typography variant="subtitle1" color="text.secondary" sx={{ mb: 1 }}>
        {profile?.email}
      </Typography>

      <Typography variant="body2" color="text.secondary" sx={{ mb: 4 }}>
        Welcome to your InboxIQ dashboard!
      </Typography>

      <Box sx={{ display: "flex", gap: 2, justifyContent: "center", flexWrap: "wrap" }}>
        <Button
          variant="contained"
          color="primary"
          onClick={() => navigate("/chat")}
        >
          Start Chat Assistant
        </Button>

        <Button
          variant="outlined"
          color="primary"
          onClick={() => alert("Direct email composer coming soon!")}
        >
          Compose Email
        </Button>

        <Button variant="outlined" color="secondary" onClick={handleLogout}>
          Logout
        </Button>
      </Box>

      // eslint-disable-next-line no-undef
      {process.env.NODE_ENV === "development" && (
        <Box sx={{ mt: 4, p: 2, bgcolor: "grey.100", borderRadius: 1 }}>
          <Typography variant="caption" display="block">
            Debug Info:
          </Typography>
          <Typography variant="caption" display="block">
            Email: {profile?.email}
          </Typography>
          <Typography variant="caption" display="block">
            Name: {profile?.name}
          </Typography>
        </Box>
      )}
    </Box>
  );
}

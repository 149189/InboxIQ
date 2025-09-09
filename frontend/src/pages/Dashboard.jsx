// src/pages/Dashboard.jsx
import React, { useEffect, useState } from "react";
import { Button, CircularProgress, Typography, Box } from "@mui/material";

export default function Dashboard() {
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const res = await fetch("http://127.0.0.1:8000/auth/oauth/profile/", {
          method: "GET",
          credentials: "include", // include cookies (sessionid)
          headers: {
            Accept: "application/json",
          },
        });

        if (!res.ok) {
          throw new Error(`Profile fetch failed: ${res.status}`);
        }

        const data = await res.json();
        setProfile(data);
      } catch (err) {
        console.error("Profile error:", err);
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchProfile();
  }, []);

  const handleLogout = async () => {
    try {
      await fetch("http://127.0.0.1:8000/auth/logout/", {
        method: "POST",
        credentials: "include",
        headers: {
          "X-CSRFToken": getCookie("csrftoken"), // if CSRF protection is enabled
        },
      });
      window.location.href = "/login";
    } catch (err) {
      console.error("Logout failed:", err);
    }
  };

  // Helper: get CSRF token from cookie
  const getCookie = (name) => {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
      const cookies = document.cookie.split(";");
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.startsWith(name + "=")) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" height="100vh">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Box textAlign="center" mt={10}>
        <Typography variant="h6" color="error">
          Failed to load profile: {error}
        </Typography>
      </Box>
    );
  }

  return (
    <Box textAlign="center" mt={10}>
      <Typography variant="h4">
        Hello {profile?.name || profile?.email} 👋
      </Typography>
      <Typography variant="subtitle1" mt={2}>
        Welcome to your dashboard!
      </Typography>

      <Box mt={4}>
        <Button variant="contained" color="secondary" onClick={handleLogout}>
          Logout
        </Button>
      </Box>
    </Box>
  );
}

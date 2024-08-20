"use client";

import Link from "next/link"; // Import Link component from Next.js
import { useState } from "react";
import { Drawer, AppBar, Toolbar, IconButton, Typography, List, ListItem, ListItemText, CssBaseline, Box } from "@mui/material";
import MenuIcon from "@mui/icons-material/Menu";

export default function Shell({ children }) {
  const [drawerOpen, setDrawerOpen] = useState(false);

  const toggleDrawer = () => {
    setDrawerOpen(!drawerOpen);
  };

  return (
    <>
      <CssBaseline />
      <AppBar position="fixed">
        <Toolbar>
          <IconButton
            edge="start"
            color="inherit"
            aria-label="menu"
            onClick={toggleDrawer}
            sx={{ mr: 2 }}
          >
            <MenuIcon />
          </IconButton>
          <Typography variant="h6" noWrap component="div">
            EK-100 Quality Annotator
          </Typography>
        </Toolbar>
      </AppBar>
      <Drawer
        anchor="left"
        open={drawerOpen}
        onClose={toggleDrawer}
      >
        <Box
          sx={{ width: 250 }}
          role="presentation"
          onClick={toggleDrawer}
          onKeyDown={toggleDrawer}
        >
          <List>
            <Link href="/" passHref>
              <ListItem button>
                <ListItemText primary="Validation Dataset" />
              </ListItem>
            </Link>
            <Link href="/my-annotations" passHref>
              <ListItem button>
                <ListItemText primary="My annotations" />
              </ListItem>
            </Link>
            <Link href="/annotate/random" passHref>
              <ListItem button>
                <ListItemText primary="Annotate" />
              </ListItem>
            </Link>
            {/* <Link href="/settings" passHref>
              <ListItem button>
                <ListItemText primary="Settings" />
              </ListItem>
            </Link> */}
          </List>
        </Box>
      </Drawer>
      <Box sx={{ display: 'flex' }}>
        <Box
          component="main"
          sx={{ flexGrow: 1, p: 3, mt: 8 }} // Adjusted margin to avoid AppBar overlap
        >
          {children}
        </Box>
      </Box>
    </>
  );
}

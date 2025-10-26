import React from "react";

const footerStyle: React.CSSProperties = {
    position: "fixed",
    left: 0,
    bottom: 0,
    width: "100%",
    zIndex: 1000,
    borderTop: "1px solid #e6e6e6",
    color: "#6b7280",
    fontSize: 13,
};

const topRowStyle: React.CSSProperties = {
    display: "flex",
    alignItems: "center",
    justifyContent: "space-between",
    gap: 8,
    background: "#ffffff", // color for the top row (logos/links)
    padding: "8px 16px",
};

const bottomRowStyle: React.CSSProperties = {
    background: "#424141", // different color for the bottom row (copyright)
    padding: "6px 16px",
    textAlign: "center" as const,
};

const linkStyle: React.CSSProperties = {
    color: "inherit",
    textDecoration: "none",
    marginLeft: 8,
    marginRight: 8,
    display: "inline-flex",
    alignItems: "center",
    gap: 8,
};

const Footer: React.FC = () => {
    return (
        <footer style={footerStyle} role="contentinfo">
            <div style={topRowStyle}>
                <a href="https://oregonstate.edu/" style={linkStyle} aria-label="Home">
                    <img src="../src/assets/OSU_logo.png" alt="OSU Logo" style={{ height: 50, verticalAlign: "middle" }} />
                    <span>Oregon State University</span>
                </a>

                <a href="https://github.com/bradfiep/CS.067-Self-Organizing-AI-Agents-at-the-Edge" style={linkStyle} aria-label="GitHub">
                    <span>GitHub</span>
                    <img src="../src/assets/github_logo.png" alt="GitHub Logo" style={{ height: 40, verticalAlign: "middle" }} />
                </a>
            </div>

            <div style={bottomRowStyle}>
                <span>© Built by Self-Organizing AI Agents at the Edge Team - Capstone 2025</span>
            </div>
        </footer>
    );
};

export default Footer;
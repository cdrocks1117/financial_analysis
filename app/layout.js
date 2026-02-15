export const metadata = {
  title: "Financial Statement Research",
  description: "Extract, normalize, and export financial statement line items.",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body
        style={{
          margin: 0,
          fontFamily: "system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
          backgroundColor: "#0f172a",
          color: "#e5e7eb",
        }}
      >
        {children}
      </body>
    </html>
  );
}


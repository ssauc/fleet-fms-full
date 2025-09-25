export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body style={{fontFamily:'system-ui, Arial, sans-serif'}}>
        <nav style={{display:'flex', gap:12, padding:12, borderBottom:'1px solid #eee'}}>
          <a href="/">Dashboard</a>
          <a href="/vehicles">Vehicles</a>
          <a href="/work-orders">Work Orders</a>
          <a href="/drivers">Drivers</a>
          <a href="/alerts">Alerts</a>
        </nav>
        {children}
      </body>
    </html>
  );
}

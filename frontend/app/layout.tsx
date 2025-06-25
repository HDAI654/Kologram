export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body style={{backgroundColor:"#212529"}}>
        {children}
      </body>
    </html>
  );
}

import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Kologram",
  description: "The Kologram app is a social media platform that allows users to share photos and videos with their friends.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>
        {children}
      </body>
    </html>
  );
}

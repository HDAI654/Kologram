import 'react-toastify/dist/ReactToastify.css';
import { ToastContainer } from 'react-toastify';
import '@/public/scroll-styles.css'

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body style={{backgroundColor:"#212529"}}>
        <ToastContainer
                position="top-right"
                autoClose={3000}
                hideProgressBar={false}
                newestOnTop={false}
                closeOnClick
                rtl={false}
                pauseOnFocusLoss
                draggable
                pauseOnHover
                theme="dark"
              />
        {children}
      </body>
    </html>
  );
}

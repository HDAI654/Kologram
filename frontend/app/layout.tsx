import { ThemeProvider } from "./contex/ThemeContext";
import "@/public/scroll-styles.css";
import "bootstrap/dist/css/bootstrap.min.css";
import "react-toastify/dist/ReactToastify.css"
import { ToastContainer } from 'react-toastify';;
import '@fortawesome/fontawesome-free/css/all.min.css';


export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
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

        <ThemeProvider>
          {children}
        </ThemeProvider>
      </body>
    </html>
  );
}
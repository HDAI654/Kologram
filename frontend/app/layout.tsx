import "bootstrap/dist/css/bootstrap.min.css";
import "react-toastify/dist/ReactToastify.css"
import { ToastContainer } from 'react-toastify';;
import '@fortawesome/fontawesome-free/css/all.min.css';
import "./global.css";
import '@/public/entry-styles.css';
import ProgressBarProvider from "./component/ProgressBarProvider";


export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" data-bs-theme="dark">
      <head>
        <script src="/bootstrap.bundle.min.js" defer></script>
      </head>
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

        <ProgressBarProvider />

        {children}

      </body>
    </html>
  );
}
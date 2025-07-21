"use client";

import { useEffect } from "react";
import { usePathname } from "next/navigation";
import NProgress from "nprogress";
import "nprogress/nprogress.css";

NProgress.configure({ showSpinner: false });

export default function ProgressBarProvider() {
  const pathname = usePathname();

  useEffect(() => {
    NProgress.start();

    // Stop after a tiny delay to simulate real loading
    const timeout = setTimeout(() => {
      NProgress.done();
    }, 300);

    return () => {
      clearTimeout(timeout);
    };
  }, [pathname]);

  return null;
}

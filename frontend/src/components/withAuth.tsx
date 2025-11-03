"use client";

import { useAuth } from "@/context/AuthContext";
import { useRouter } from "next/navigation";
import { useEffect, ComponentType } from "react";

export default function withAuth<P extends object>(
  WrappedComponent: ComponentType<P>
) {
  const WithAuth = (props: P) => {
    const { token } = useAuth();
    const router = useRouter();

    useEffect(() => {
      if (!token) {
        router.push("/login");
      }
    }, [token, router]);

    if (!token) {
      return null; // or a loading spinner
    }

    return <WrappedComponent {...props} />;
  };

  return WithAuth;
}

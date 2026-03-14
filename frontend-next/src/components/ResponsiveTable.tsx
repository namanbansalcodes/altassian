"use client";
import { useRef, useState, useEffect, useCallback } from "react";

interface ResponsiveTableProps {
  children: React.ReactNode;
  className?: string;
  label?: string;
  bg?: "card" | "surface";
}

const gradientColors = {
  card: "from-white dark:from-neutral-900",
  surface: "from-neutral-50 dark:from-neutral-950",
};

export default function ResponsiveTable({
  children,
  className = "",
  label = "Scrollable table",
  bg = "card",
}: ResponsiveTableProps) {
  const scrollRef = useRef<HTMLDivElement>(null);
  const [canScrollLeft, setCanScrollLeft] = useState(false);
  const [canScrollRight, setCanScrollRight] = useState(false);

  const updateScrollState = useCallback(() => {
    const el = scrollRef.current;
    if (!el) return;
    setCanScrollLeft(el.scrollLeft > 1);
    setCanScrollRight(el.scrollLeft + el.clientWidth < el.scrollWidth - 1);
  }, []);

  useEffect(() => {
    const el = scrollRef.current;
    if (!el) return;
    updateScrollState();
    el.addEventListener("scroll", updateScrollState, { passive: true });
    const ro = new ResizeObserver(updateScrollState);
    ro.observe(el);
    return () => {
      el.removeEventListener("scroll", updateScrollState);
      ro.disconnect();
    };
  }, [updateScrollState]);

  const from = gradientColors[bg];
  const scrollHint =
    canScrollLeft || canScrollRight
      ? `${label} — scroll horizontally to see more`
      : label;

  return (
    <div className={`relative ${className}`} role="region" aria-label={label}>
      {canScrollLeft && (
        <div
          className={`absolute left-0 top-0 bottom-0 w-4 sm:w-6 bg-gradient-to-r ${from} to-transparent z-10 pointer-events-none`}
          aria-hidden="true"
        />
      )}
      {canScrollRight && (
        <div
          className={`absolute right-0 top-0 bottom-0 w-4 sm:w-6 bg-gradient-to-l ${from} to-transparent z-10 pointer-events-none`}
          aria-hidden="true"
        />
      )}
      <div
        ref={scrollRef}
        tabIndex={0}
        className="overflow-x-auto -mx-4 sm:-mx-6 md:mx-0 scrollbar-thin"
        aria-label={scrollHint}
      >
        <div className="inline-block min-w-full px-4 sm:px-6 md:px-0 align-middle">
          {children}
        </div>
      </div>
    </div>
  );
}

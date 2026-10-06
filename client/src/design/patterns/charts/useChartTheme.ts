"use client";

import { useEffect, useState } from "react";

import {
  prefersReducedMotion,
  readChartTheme,
  type ChartTheme,
} from "@/design/patterns/charts/theme";

/** Client chart theme + motion preference; re-reads on theme attribute changes. */
export function useChartTheme() {
  const [theme, setTheme] = useState<ChartTheme>(() => readChartTheme());
  const [reduceMotion, setReduceMotion] = useState(false);

  useEffect(() => {
    const sync = () => {
      setTheme(readChartTheme());
      setReduceMotion(prefersReducedMotion());
    };
    sync();
    const obs = new MutationObserver(sync);
    obs.observe(document.documentElement, {
      attributes: true,
      attributeFilter: ["data-theme", "class"],
    });
    const mq = window.matchMedia("(prefers-reduced-motion: reduce)");
    const onMq = () => setReduceMotion(mq.matches);
    mq.addEventListener("change", onMq);
    return () => {
      obs.disconnect();
      mq.removeEventListener("change", onMq);
    };
  }, []);

  return { theme, reduceMotion };
}

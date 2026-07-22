"use client";

// Custom dropdown replacing native <select>: the native popup is OS-rendered
// (overlaps the trigger, blue highlight) and can't match the design system.
// Panel opens below the trigger, full trigger width, warm palette only.

import { useEffect, useId, useRef, useState } from "react";
import { Check, ChevronDown } from "lucide-react";

export type SelectOption = { value: string; label: string };

export default function Select({
  value,
  onChange,
  options,
  ariaLabel,
  width,
  triggerStyle,
}: {
  value: string;
  onChange: (value: string) => void;
  options: SelectOption[];
  ariaLabel?: string;
  width?: number | string;
  /** Merged into the trigger button, e.g. to match an adjacent input's size. */
  triggerStyle?: React.CSSProperties;
}) {
  const [open, setOpen] = useState(false);
  const [activeIndex, setActiveIndex] = useState(-1);
  const rootRef = useRef<HTMLDivElement>(null);
  const listboxId = useId();
  const selected = options.find((o) => o.value === value);

  useEffect(() => {
    if (!open) return;
    const onPointerDown = (e: PointerEvent) => {
      if (rootRef.current && !rootRef.current.contains(e.target as Node)) {
        setOpen(false);
      }
    };
    document.addEventListener("pointerdown", onPointerDown);
    return () => document.removeEventListener("pointerdown", onPointerDown);
  }, [open]);

  const openPanel = () => {
    setActiveIndex(Math.max(0, options.findIndex((o) => o.value === value)));
    setOpen(true);
  };

  const commit = (index: number) => {
    const option = options[index];
    if (option) onChange(option.value);
    setOpen(false);
  };

  const onKeyDown = (e: React.KeyboardEvent) => {
    if (!open) {
      if (["Enter", " ", "ArrowDown", "ArrowUp"].includes(e.key)) {
        e.preventDefault();
        openPanel();
      }
      return;
    }
    if (e.key === "Escape") {
      e.preventDefault();
      setOpen(false);
    } else if (e.key === "ArrowDown") {
      e.preventDefault();
      setActiveIndex((i) => Math.min(options.length - 1, i + 1));
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      setActiveIndex((i) => Math.max(0, i - 1));
    } else if (e.key === "Enter" || e.key === " ") {
      e.preventDefault();
      commit(activeIndex);
    } else if (e.key === "Tab") {
      setOpen(false);
    }
  };

  return (
    <div ref={rootRef} style={{ position: "relative", width, minWidth: 0 }}>
      <button
        type="button"
        aria-haspopup="listbox"
        aria-expanded={open}
        aria-controls={open ? listboxId : undefined}
        aria-label={ariaLabel}
        onClick={() => (open ? setOpen(false) : openPanel())}
        onKeyDown={onKeyDown}
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          gap: 8,
          width: "100%",
          fontSize: 13,
          padding: "7px 10px",
          borderRadius: 8,
          border: `1px solid ${open ? "#F04E0D" : "#E8E2DB"}`,
          backgroundColor: "#FAF8F5",
          color: "#1B1817",
          fontFamily: "inherit",
          cursor: "pointer",
          textAlign: "left",
          ...triggerStyle,
        }}
      >
        <span style={{ overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
          {selected?.label ?? ""}
        </span>
        <ChevronDown
          size={14}
          color="#6E6660"
          style={{
            flexShrink: 0,
            transition: "transform 120ms ease",
            transform: open ? "rotate(180deg)" : "none",
          }}
        />
      </button>
      {open && (
        <ul
          id={listboxId}
          role="listbox"
          aria-label={ariaLabel}
          style={{
            position: "absolute",
            top: "calc(100% + 6px)",
            left: 0,
            minWidth: "100%",
            margin: 0,
            padding: 4,
            listStyle: "none",
            backgroundColor: "#FFFFFF",
            border: "1px solid #E8E2DB",
            borderRadius: 10,
            boxShadow: "0 8px 24px rgba(27, 24, 23, 0.10)",
            zIndex: 50,
            maxHeight: 280,
            overflowY: "auto",
          }}
        >
          {options.map((option, i) => {
            const isSelected = option.value === value;
            const isActive = i === activeIndex;
            return (
              <li
                key={option.value}
                role="option"
                aria-selected={isSelected}
                onPointerEnter={() => setActiveIndex(i)}
                onClick={() => commit(i)}
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: 8,
                  fontSize: 13,
                  padding: "7px 10px",
                  borderRadius: 6,
                  cursor: "pointer",
                  whiteSpace: "nowrap",
                  color: isSelected ? "#1B1817" : "#3A3531",
                  fontWeight: isSelected ? 600 : 400,
                  backgroundColor: isActive ? "#F6F4F1" : "transparent",
                }}
              >
                <span style={{ width: 14, flexShrink: 0, display: "inline-flex" }}>
                  {isSelected && <Check size={14} color="#F04E0D" />}
                </span>
                {option.label}
              </li>
            );
          })}
        </ul>
      )}
    </div>
  );
}

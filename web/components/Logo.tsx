import { cn } from "@/lib/utils";

type LogoProps = {
  size?: number;
  className?: string;
  spin?: boolean;
};

/**
 * whendo logo — 14 petals arranged in a circle, morphing from long-thin
 * (top-left) to short-round (right). The asymmetry and the visible gap
 * at the top give the mark its character.
 *
 * `currentColor` is used so it inherits from the parent's text color
 * (white in dark mode, etc.). Pass `spin` for a slow rotation animation.
 */
export function Logo({ size = 32, className, spin = false }: LogoProps) {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 200 200"
      width={size}
      height={size}
      fill="currentColor"
      aria-label="whendo"
      role="img"
      className={cn(spin && "[animation:spin_20s_linear_infinite]", className)}
    >
      <g transform="translate(100 106)">
        <g transform="rotate(-5)"><ellipse cy="-44" rx="4.4" ry="30.6" /></g>
        <g transform="rotate(-22)"><ellipse cy="-44" rx="4.7" ry="26.6" /></g>
        <g transform="rotate(-42)"><ellipse cy="-44" rx="5.0" ry="23.3" /></g>
        <g transform="rotate(-64)"><ellipse cy="-44" rx="5.4" ry="20.0" /></g>
        <g transform="rotate(-88)"><ellipse cy="-45" rx="5.7" ry="17.4" /></g>
        <g transform="rotate(-114)"><ellipse cy="-45" rx="6.0" ry="15.0" /></g>
        <g transform="rotate(-142)"><ellipse cy="-46" rx="6.3" ry="13.4" /></g>
        <g transform="rotate(-170)"><ellipse cy="-46" rx="6.7" ry="12.7" /></g>
        <g transform="rotate(162)"><ellipse cy="-46" rx="7.0" ry="11.7" /></g>
        <g transform="rotate(136)"><ellipse cy="-45" rx="7.7" ry="11.0" /></g>
        <g transform="rotate(110)"><ellipse cy="-43" rx="8.3" ry="10.7" /></g>
        <g transform="rotate(84)"><ellipse cy="-43" rx="8.7" ry="10.0" /></g>
        <g transform="rotate(56)"><ellipse cy="-43" rx="8.3" ry="10.0" /></g>
        <g transform="rotate(32)"><ellipse cy="-45" rx="7.4" ry="11.7" /></g>
      </g>
    </svg>
  );
}

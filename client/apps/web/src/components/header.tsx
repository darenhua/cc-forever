import { Link } from "@tanstack/react-router";
import { Menu } from "lucide-react";
import { ModeToggle } from "./mode-toggle";
import { Button } from "@/components/ui/button";
import { useSheetState } from "./sheet-provider";

export default function Header() {
	const links = [{ to: "/second", label: "HardestWorkingGameDev" }] as const;
	const { setIsOpen } = useSheetState();

	return (
		<div className="">
			<div className="flex flex-row items-center justify-between px-2 py-1">
				<nav className="flex gap-4 text-lg">
					{links.map(({ to, label }) => {
						return (
							<Link key={to} to={to}>
								<p className="text-lg font-bold">{label}</p>
							</Link>
						);
					})}
				</nav>
				<div className="flex items-center gap-2">
					<Button variant="ghost" size="icon" onClick={() => setIsOpen(true)}>
						<Menu className="h-[1.2rem] w-[1.2rem]" />
						<span className="sr-only">Open menu</span>
					</Button>
					<ModeToggle />
				</div>
			</div>
			<hr />
		</div>
	);
}

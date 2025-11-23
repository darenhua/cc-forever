import { useSheetState } from "@/components/sheet-provider";
import { useEffect, useState } from "react";
import {
	Sheet,
	SheetContent,
	SheetHeader,
	SheetTitle,
	SheetDescription,
} from "@/components/ui/sheet";

export default function AgentsSheet() {
	const { isOpen, setIsOpen } = useSheetState();
	const [session, setSession] = useState(null);

	// Fetch session data when sheet opens
	useEffect(() => {
		if (isOpen) {
			const fetchSession = async () => {
				try {
					const response = await fetch('http://localhost:8000/stats');
					const data = await response.json();
					
					if (data.session !== undefined) {
						setSession(data.usage_stats.session);
						// You could also store it elsewhere if needed
						console.log('Session ID:', data.usage_stats.session);
					}
				} catch (error) {
					console.error('Error fetching session:', error);
				}
			};

			fetchSession();
		}
	}, [isOpen]); // This effect runs whenever isOpen changes

	return (
		<Sheet open={isOpen} onOpenChange={setIsOpen}>
			<SheetContent>
				<SheetHeader>
					<SheetTitle>Menu</SheetTitle>
					<SheetDescription>
						Your menu content goes here.
						{session !== null && (
							<div>Current Session: {session}</div>
						)}
					</SheetDescription>
				</SheetHeader>
			</SheetContent>
		</Sheet>
	);
}

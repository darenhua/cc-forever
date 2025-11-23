import { useSheetState } from "@/components/sheet-provider";
import {
	Sheet,
	SheetContent,
	SheetHeader,
	SheetTitle,
	SheetDescription,
} from "@/components/ui/sheet";

export default function AgentsSheet() {
	const { isOpen, setIsOpen } = useSheetState();

	return (
		<Sheet open={isOpen} onOpenChange={setIsOpen}>
			<SheetContent>
				<SheetHeader>
					<SheetTitle>Menu</SheetTitle>
					<SheetDescription>
						Your menu content goes here.
					</SheetDescription>
				</SheetHeader>
			</SheetContent>
		</Sheet>
	);
}

import { createContext, useContext, useState } from "react";
import type { ReactNode } from "react";

type SheetContextType = {
	isOpen: boolean;
	setIsOpen: (open: boolean) => void;
};

const SheetContext = createContext<SheetContextType | undefined>(undefined);

export function SheetProvider({ children }: { children: ReactNode }) {
	const [isOpen, setIsOpen] = useState(false);

	return (
		<SheetContext.Provider value={{ isOpen, setIsOpen }}>
			{children}
		</SheetContext.Provider>
	);
}

export function useSheetState() {
	const context = useContext(SheetContext);
	if (context === undefined) {
		throw new Error("useSheetState must be used within a SheetProvider");
	}
	return context;
}

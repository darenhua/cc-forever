import { createFileRoute, Link } from "@tanstack/react-router";

export const Route = createFileRoute("/second")({
	component: Page,
});

function Page() {
	return (
		<div className="">
			<div >
				<h1>Hello World</h1>
			</div>
		</div>
	)
}
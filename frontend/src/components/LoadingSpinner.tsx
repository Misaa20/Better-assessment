export function LoadingSpinner() {
  return (
    <div className="flex items-center justify-center py-12">
      <div className="h-5 w-5 animate-spin rounded-full border-2 border-gray-200 border-t-gray-600" />
    </div>
  );
}

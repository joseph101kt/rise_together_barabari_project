import ResourceCard from "./ResourceCard";

const ModuleSection = ({
  module,
  resources,
  enrolled = false,
  submittedLinks = [],
  onToggleLink,
  onOpenSubmitModal,
}) => {
  return (
    <section className="mb-12">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900">
          {module.title}
        </h2>

        {module.description && (
          <p className="mt-2 text-gray-600">
            {module.description}
          </p>
        )}
      </div>

      {resources.length > 0 ? (
        <div className="grid gap-6 md:grid-cols-2">
          {resources.map((resource) => (
            <ResourceCard
              key={resource.id}
              resource={resource}
              enrolled={enrolled}
              submittedLinks={submittedLinks}
              onToggleLink={onToggleLink}
              onOpenSubmitModal={onOpenSubmitModal}
            />
          ))}
        </div>
      ) : (
        <div className="rounded-xl border border-dashed p-6 text-gray-500">
          No resources available yet.
        </div>
      )}
    </section>
  );
};

export default ModuleSection;
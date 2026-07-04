import API from "../lib/api";

export const userService = {
  /*
   Get the logged-in user's full profile
   */
  getMyProfile: async () => {
    const response = await API.get("/users/self");
    return response.data;
  },

  /*
    Update profile information, education, experience, or external links
   */
  updateMyProfile: async (updateData) => {
    const response = await API.patch("/users/self", updateData);
    return response.data;
  },

  /**
   * Add skills to a user's profile
   */
  addSkills: async (userId, skillIds) => {
    const response = await API.post(`/users/${userId}/skills`, {
      skill_ids: skillIds,
    });
    return response.data;
  },

  removeSkill: async (userId, skillId) => {
    const response = await API.delete(`/users/${userId}/skills/${skillId}`);
    return response.data;
  },
};

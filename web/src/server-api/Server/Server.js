import axios from "axios";
import * as HttpStatus from "http-status-codes";
import Transform from "./Transform";
import { Response } from "../Response";
import fileFiltersToQueryParams from "./helpers/fileFiltersToQueryParams";
import clusterFiltersToQueryParams from "./helpers/clusterFiltersToQueryParams";
import matchesFiltersToQueryParams from "./helpers/matchesFiltersToQueryParams";

export default class Server {
  constructor({ baseURL = "/api/v1", timeout = 10 * 1000, headers = {} } = {}) {
    this.axios = axios.create({
      baseURL,
      timeout,
      headers,
    });
    this.transform = new Transform();
  }

  async fetchFiles({ limit, offset, filters }) {
    try {
      const response = await this.axios.get("/files/", {
        params: {
          offset,
          limit,
          include: ["signature", "meta", "exif"].join(","),
          ...fileFiltersToQueryParams(filters),
        },
      });
      const data = this.transform.fetchFileResults(response.data);
      return Response.ok(data);
    } catch (error) {
      return this.errorResponse(error);
    }
  }

  async fetchFile({ id }) {
    try {
      const response = await this.axios.get(`/files/${id}`, {
        params: {
          include: ["signature", "meta", "scenes", "exif"].join(","),
        },
      });
      const data = this.transform.videoFile(response.data);
      return Response.ok(data);
    } catch (error) {
      return this.errorResponse(error);
    }
  }

  async fetchFileCluster({
    fileId,
    limit = 20,
    offset = 0,
    fields = [],
    filters,
  }) {
    try {
      const response = await this.axios.get(`/files/${fileId}/cluster`, {
        params: {
          limit,
          offset,
          ...clusterFiltersToQueryParams({ filters, fields }),
        },
      });
      const data = this.transform.fetchFileClusterResults(response.data);
      return Response.ok(data);
    } catch (error) {
      return this.errorResponse(error);
    }
  }

  async fetchFileMatches({
    fileId,
    limit = 20,
    offset = 0,
    fields = ["meta", "exif", "scenes"],
    filters = {},
  }) {
    try {
      const response = await this.axios.get(`/files/${fileId}/matches`, {
        params: {
          limit,
          offset,
          ...matchesFiltersToQueryParams({ filters, fields }),
        },
      });
      const data = this.transform.fetchFileMatchesResults(response.data);
      return Response.ok(data);
    } catch (error) {
      return this.errorResponse(error);
    }
  }

  async probeVideoFile({ id }) {
    try {
      await this.axios.head(`/files/${id}/watch`);
      return Response.ok(null);
    } catch (error) {
      return this.errorResponse(error);
    }
  }

  async rayHeadNodeLaunch(ipaddr){
    try {
      const response = await this.axios.get(`/head/${ipaddr}`);
      return Response.ok(response);
    } catch (error) {
      return this.errorResponse(error);
    } 
  }

  async rayWorkerNodeLaunch(ipaddr){
    try {
      const response = await this.axios.get(`/worker/${ipaddr}`);
      return Response.ok(response);
    } catch (error) {
      return this.errorResponse(error);
    }  
  }

  async rayNodeStop(ipaddr){
    try {
      const response = await this.axios.get(`/ray_stop/${ipaddr}`);
      return Response.ok(response);
    } catch (error) {
      return this.errorResponse(error);
    }   
  }

  async rayNodeClean(ipaddr){
    try {
      const response = await this.axios.get(`/clean/${ipaddr}`);
      return Response.ok(response);
    } catch (error) {
      return this.errorResponse(error);
    }   
  }

  async rayTaskLaunch(startTime, endTime){
    try{
      const response = await this.axios.get(`/launch/${startTime}-${endTime}`);
      return Response.ok(response); 
    }catch (error) {
      return this.errorResponse(error);
    }   
  }

  async rayTaskStop(){
    try{
      const response = await this.axios.get(`/task_stop/`);
      return Response.ok(response); 
    }catch (error) {
      return this.errorResponse(error);
    }    
  }

  errorResponse(error) {
    if (error.response == null) {
      return Response.clientError(error);
    }
    const response = error.response;
    switch (response.status) {
      case HttpStatus.BAD_REQUEST:
        return Response.invalid(error);
      case HttpStatus.UNAUTHORIZED:
        return Response.unauthorized(error);
      case HttpStatus.NOT_FOUND:
        return Response.notFound(error);
      default:
        return Response.clientError(error);
    }
  }
}
